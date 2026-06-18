"""Hardened XML parse engine, stdlib-only.

Built directly on ``xml.parsers.expat`` + ``xml.etree.ElementTree.TreeBuilder``
(measure-first F5: the CPython C-accelerated ``ElementTree.XMLParser`` does not
expose its underlying expat parser, so the blocking handlers cannot be installed
on it; defusedxml's workaround imports the *pure-Python* parser via fragile module
surgery, which this avoids).

``XMLParser`` mirrors the stdlib ``XMLParser`` expat→tree glue (namespace separator
``"}"``, ordered attributes, buffered text, Clark-notation name fixup,
undefined-entity handling) so the resulting ``Element`` tree is identical to the
stdlib's / defusedxml's, and installs blocking handlers per the ``forbid_*`` flags
(defaults match defusedxml: ``forbid_dtd=False, forbid_entities=True,
forbid_external=True``). It exposes ``feed``/``close`` so it is drop-in for
``xml.etree.ElementTree.parse(source, parser=...)``.
"""
from __future__ import annotations

import xml.parsers.expat as _expat
from collections.abc import Iterable, Iterator
from typing import IO, Any, Protocol
from xml.etree.ElementTree import Element, ElementTree, ParseError, TreeBuilder
from xml.etree.ElementTree import iterparse as _stdlib_iterparse
from xml.etree.ElementTree import parse as _stdlib_parse

from .errors import (
    AttributesExceeded,
    DepthExceeded,
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    SizeExceeded,
)
from .limits import Limits

__all__ = ["XMLParser", "fromstring", "parse", "fromstringlist", "iterparse"]


class _PathLike(Protocol):
    """Structural match for ``os.PathLike`` (e.g. ``pathlib.Path``) — so `parse`/
    `iterparse` accept path objects without importing the I/O-guard-forbidden ``os``."""

    def __fspath__(self) -> str | bytes: ...


class XMLParser:
    """Hardened drop-in for ``xml.etree.ElementTree.XMLParser`` / defusedxml's
    ``DefusedXMLParser``. ``feed()``/``close()`` are compatible with
    ``xml.etree.ElementTree.parse``.
    """

    def __init__(self, *, target: Any = None, encoding: str | None = None,
                 forbid_dtd: bool = False, forbid_entities: bool = True,
                 forbid_external: bool = True, limits: Limits | None = None) -> None:
        parser = _expat.ParserCreate(encoding, "}")
        self.parser = parser
        self.target = target if target is not None else TreeBuilder()
        self._error = _expat.error
        self._names: dict[str, str] = {}
        self.entity: dict[str, str] = {}  # always empty when forbid_entities (every decl blocked)

        # --- opt-in structural-DoS limits (v0.4 mirror-plus; None == no cap) ---
        # Extracted to scalars so the default path is a cheap `is not None` check.
        self._max_depth = limits.max_depth if limits else None
        self._max_attributes = limits.max_attributes if limits else None
        self._max_bytes = limits.max_bytes if limits else None
        self._depth = 0
        self._fed = 0

        # --- tree-building glue (mirrors stdlib xml.etree XMLParser) ---
        # Guard the optional target callbacks with hasattr, like the stdlib, so a
        # custom target providing only the core protocol (start/end/data/close)
        # works (a default TreeBuilder has all of these). BUT: depth/attribute caps
        # are purexml's own accounting and must NOT depend on the target's callbacks
        # — so install _start/_end whenever a cap needs them, and `_start`/`_end`
        # call the target only if it provides start/end (PR#7 Codex: a target with
        # `start` but no `end` otherwise never decremented depth).
        self._has_start = hasattr(self.target, "start")
        self._has_end = hasattr(self.target, "end")
        parser.DefaultHandlerExpand = self._default
        if self._has_start or self._max_depth is not None or self._max_attributes is not None:
            parser.StartElementHandler = self._start
        if self._has_end or self._max_depth is not None:
            parser.EndElementHandler = self._end
        if hasattr(self.target, "data"):
            parser.CharacterDataHandler = self.target.data
        if hasattr(self.target, "comment"):
            parser.CommentHandler = self.target.comment
        if hasattr(self.target, "pi"):
            parser.ProcessingInstructionHandler = self.target.pi
        parser.buffer_text = 1       # type: ignore[assignment]  # verbatim stdlib value (1, not True)
        parser.ordered_attributes = 1  # type: ignore[assignment]

        # --- security handlers (defusedxml-equivalent, per the flags) ---
        if forbid_dtd:
            parser.StartDoctypeDeclHandler = self._forbid_dtd
        if forbid_entities:
            parser.EntityDeclHandler = self._forbid_entity_decl
            parser.UnparsedEntityDeclHandler = self._forbid_unparsed_entity_decl
        if forbid_external:
            parser.ExternalEntityRefHandler = self._forbid_external_ref

    # ---- blocking handlers ----
    def _forbid_dtd(self, name, sysid, pubid, has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def _forbid_entity_decl(self, name, is_parameter_entity, value, base,
                            sysid, pubid, notation_name):
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_external_ref(self, context, base, sysid, pubid):
        raise ExternalReferenceForbidden(sysid, pubid)

    # ---- tree-building glue ----
    def _fixname(self, key):
        try:
            return self._names[key]
        except KeyError:
            name = key
            if "}" in name:
                name = "{" + name
            self._names[key] = name
            return name

    def _start(self, tag, attr_list):
        fixname = self._fixname
        tag = fixname(tag)
        # opt-in structural caps — purexml's own accounting, independent of target
        if self._max_attributes is not None and attr_list:
            nattrs = len(attr_list) // 2
            if nattrs > self._max_attributes:
                raise AttributesExceeded(tag, nattrs, self._max_attributes)
        if self._max_depth is not None:
            self._depth += 1
            if self._depth > self._max_depth:
                raise DepthExceeded(self._depth, self._max_depth)
        if not self._has_start:  # installed only for cap accounting; nothing to build
            return None
        attrib = {}
        if attr_list:
            for i in range(0, len(attr_list), 2):
                attrib[fixname(attr_list[i])] = attr_list[i + 1]
        return self.target.start(tag, attrib)

    def _end(self, tag):
        if self._max_depth is not None:
            self._depth -= 1
        if self._has_end:
            return self.target.end(self._fixname(tag))
        return None

    def _start_ns(self, prefix, uri):
        return self.target.start_ns(prefix or "", uri or "")

    def _end_ns(self, prefix):
        return self.target.end_ns(prefix or "")

    # ---- incremental event API (drives stdlib iterparse / XMLPullParser) ----
    def _setevents(self, events_queue, events_to_report):
        # Internal API used by xml.etree's XMLPullParser/iterparse. Faithful mirror
        # of the stdlib XMLParser._setevents (wires expat handlers to append
        # (event, data) to the queue). The blocking handlers installed in __init__
        # are NOT touched here, so hardening stays active during incremental feed.
        parser = self.parser
        append = events_queue.append
        for event_name in events_to_report:
            if event_name == "start":
                parser.ordered_attributes = 1

                # NB: _setevents is a verbatim mirror of CPython XMLParser._setevents;
                # the per-event `handler` redefinitions are deliberate (do not rename —
                # see Known decisions). mypy flags the redefinitions; ignore[misc] them.
                def handler(tag, attrib_in, event=event_name, append=append,
                            start=self._start):
                    append((event, start(tag, attrib_in)))
                parser.StartElementHandler = handler
            elif event_name == "end":
                def handler(tag, event=event_name, append=append, end=self._end):  # type: ignore[misc]
                    append((event, end(tag)))
                parser.EndElementHandler = handler
            elif event_name == "start-ns":
                if hasattr(self.target, "start_ns"):
                    def handler(prefix, uri, event=event_name, append=append,
                                start_ns=self._start_ns):
                        append((event, start_ns(prefix, uri)))
                else:
                    def handler(prefix, uri, event=event_name, append=append):  # type: ignore[misc]
                        append((event, (prefix or "", uri or "")))
                parser.StartNamespaceDeclHandler = handler
            elif event_name == "end-ns":
                if hasattr(self.target, "end_ns"):
                    def handler(prefix, event=event_name, append=append,  # type: ignore[misc]
                                end_ns=self._end_ns):
                        append((event, end_ns(prefix)))
                else:
                    def handler(prefix, event=event_name, append=append):  # type: ignore[misc]
                        append((event, None))
                parser.EndNamespaceDeclHandler = handler
            elif event_name == "comment":
                def handler(text, event=event_name, append=append, self=self):  # type: ignore[misc]
                    append((event, self.target.comment(text)))
                parser.CommentHandler = handler
            elif event_name == "pi":
                def handler(pi_target, data, event=event_name, append=append, self=self):
                    append((event, self.target.pi(pi_target, data)))
                parser.ProcessingInstructionHandler = handler
            else:
                raise ValueError("unknown event %r" % event_name)

    def _default(self, text):
        # Mirrors the stdlib: a reference to an entity that was never defined raises
        # an undefined-entity error (surfaced as ParseError). With forbid_entities,
        # self.entity is always empty, so any non-predefined entity reference lands
        # here and raises — matching defusedxml. Predefined entities (&amp; etc.) are
        # resolved by expat and never reach this handler. DOCTYPE text is ignored
        # (TreeBuilder has no doctype hook).
        if text[:1] == "&":
            try:
                self.target.data(self.entity[text[1:-1]])
            except KeyError:
                err = self._error(
                    "undefined entity %s: line %d, column %d"
                    % (text, self.parser.ErrorLineNumber,
                       self.parser.ErrorColumnNumber)
                )
                err.code = 11  # XML_ERROR_UNDEFINED_ENTITY
                err.lineno = self.parser.ErrorLineNumber
                err.offset = self.parser.ErrorColumnNumber
                raise err

    def _raiseerror(self, value):
        err = ParseError(value)
        err.code = value.code
        err.position = (value.lineno, value.offset)
        raise err

    def _cleanup(self):
        # Break the expat-parser <-> self reference cycle (handlers are bound
        # methods of self) so the parser+tree are freed by refcounting, not cyclic
        # GC. Must run on EVERY termination path — success or error — or a malformed
        # / blocked untrusted input leaks the cycle (v0.1.2 fix; regressed and
        # restored after the v0.2 feed/close split, PR#4 review).
        self.parser = None
        self.target = None

    # ---- feed/close (compatible with xml.etree.ElementTree.parse) ----
    def feed(self, data: str | bytes) -> None:
        if self._max_bytes is not None:
            # Count true bytes (PR#7 Codex): a str chunk is measured by its UTF-8
            # byte length, not code-point count, so the documented byte cap can't be
            # bypassed by multi-byte input. (The str is already materialized by the
            # caller, so encoding-to-measure adds no new DoS surface.)
            self._fed += len(data) if isinstance(data, (bytes, bytearray)) \
                else len(data.encode("utf-8"))
            if self._fed > self._max_bytes:
                self._cleanup()
                raise SizeExceeded(self._fed, self._max_bytes)
        try:
            self.parser.Parse(data, False)
        except self._error as v:
            self._cleanup()
            self._raiseerror(v)
        except BaseException:
            # blocking refusals (EntitiesForbidden / LimitExceeded / ...) and anything else
            self._cleanup()
            raise

    def close(self) -> Any:  # returns the target's result (Element for the default)
        try:
            try:
                self.parser.Parse(b"", True)
            except self._error as v:
                self._raiseerror(v)
            return self.target.close()
        finally:
            self._cleanup()


def fromstring(text: str | bytes, forbid_dtd: bool = False,
               forbid_entities: bool = True, forbid_external: bool = True,
               *, limits: Limits | None = None) -> Element:
    """Parse XML *text* into an ``xml.etree.ElementTree.Element``, safely.

    Behaviorally equivalent to ``defusedxml.ElementTree.fromstring``: entity
    declarations and external reference resolution are blocked (raising
    ``EntitiesForbidden`` / ``ExternalReferenceForbidden``, both ``ValueError``
    subclasses); ``forbid_dtd=True`` additionally blocks any DOCTYPE
    (``DTDForbidden``); malformed input raises ``xml.etree.ElementTree.ParseError``.
    Stdlib-only.

    *limits* (purexml mirror-plus; keyword-only, default ``None`` = no caps = strict
    mirror): an opt-in ``purexml.Limits`` bounding structural DoS — exceeding a cap
    raises a ``LimitExceeded`` subclass.
    """
    parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                       forbid_external=forbid_external, limits=limits)
    parser.feed(text)
    return parser.close()


def parse(source: str | bytes | _PathLike | IO[Any], parser: XMLParser | None = None,
          forbid_dtd: bool = False, forbid_entities: bool = True,
          forbid_external: bool = True, *, limits: Limits | None = None) -> ElementTree:
    """Parse XML from *source* (a filename or file-like) into a hardened
    ``ElementTree``. Mirrors ``defusedxml.ElementTree.parse``. *limits* (opt-in,
    keyword-only) applies only when building the default parser."""
    if parser is None:
        # We own the parser: guarantee its cycle is broken even if the source read
        # raises before feed/close run (PR#7 Gemini). When a caller passes `parser`,
        # they own its lifecycle.
        parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                           forbid_external=forbid_external, limits=limits)
        try:
            # purexml.XMLParser is a structural drop-in for the stdlib parser
            # (feed/close), not a nominal subclass — typeshed can't express that.
            return _stdlib_parse(source, parser)  # type: ignore[arg-type, return-value]
        finally:
            if parser.parser is not None:  # not already cleaned by feed/close
                parser._cleanup()
    return _stdlib_parse(source, parser)  # type: ignore[arg-type, return-value]


def fromstringlist(sequence: Iterable[str | bytes], parser: XMLParser | None = None,
                   forbid_dtd: bool = False, forbid_entities: bool = True,
                   forbid_external: bool = True, *,
                   limits: Limits | None = None) -> Element:
    """Parse a *sequence* of XML string fragments into an ``Element``, safely.

    Stdlib-parity addition (``defusedxml.ElementTree`` does not provide
    ``fromstringlist``); behaves like a hardened ``xml.etree.ElementTree``
    ``fromstringlist`` — equivalent to ``fromstring("".join(sequence))``. *limits*
    (opt-in, keyword-only) applies only when building the default parser.
    """
    if parser is None:
        # We own the parser: clean up even if iterating `sequence` raises mid-stream
        # before close() runs (PR#7 Gemini).
        own = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                        forbid_external=forbid_external, limits=limits)
        try:
            for text in sequence:
                own.feed(text)
            return own.close()
        finally:
            if own.parser is not None:
                own._cleanup()
    for text in sequence:
        parser.feed(text)
    return parser.close()


def iterparse(source: str | bytes | _PathLike | IO[Any], events: Iterable[str] | None = None,
              parser: XMLParser | None = None, forbid_dtd: bool = False,
              forbid_entities: bool = True, forbid_external: bool = True,
              *, limits: Limits | None = None) -> Iterator[tuple[str, Any]]:
    """Incrementally parse XML from *source*, yielding ``(event, elem)`` pairs, safely.

    Mirrors ``defusedxml.ElementTree.iterparse``. Reuses the stdlib `iterparse`
    iterator driving purexml's hardened `XMLParser` via `_setevents` — so the
    blocking handlers fire *during* the incremental feed (bombs/XXE are blocked at
    the declaration mid-stream, before the consumer iterates past them), and the
    parser's error/close cleanup releases the heavy state. Default events: `"end"`.

    Note: if a caller abandons the iterator before EOF (an early ``break``), the
    parser + partial tree are reclaimed by cyclic GC rather than promptly — the
    stdlib `iterparse` iterator only closes the parser at EOF, so this matches
    ``defusedxml.ElementTree.iterparse`` exactly (prompt early-break cleanup is a
    possible mirror-plus improvement; see scratch/spinoff_ideas.md).
    """
    if parser is None:
        parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                           forbid_external=forbid_external, limits=limits)
    # structural drop-in parser (see parse()); typeshed's iterparse is nominally typed.
    return _stdlib_iterparse(source, events, parser)  # type: ignore[call-overload]
