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
import xml.parsers.expat as _expat
from xml.etree.ElementTree import ParseError, TreeBuilder
from xml.etree.ElementTree import iterparse as _stdlib_iterparse
from xml.etree.ElementTree import parse as _stdlib_parse

from .errors import DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden

__all__ = ["XMLParser", "fromstring", "parse", "fromstringlist", "iterparse"]


class XMLParser:
    """Hardened drop-in for ``xml.etree.ElementTree.XMLParser`` / defusedxml's
    ``DefusedXMLParser``. ``feed()``/``close()`` are compatible with
    ``xml.etree.ElementTree.parse``.
    """

    def __init__(self, *, target=None, encoding=None, forbid_dtd=False,
                 forbid_entities=True, forbid_external=True):
        parser = _expat.ParserCreate(encoding, "}")
        self.parser = parser
        self.target = target if target is not None else TreeBuilder()
        self._error = _expat.error
        self._names = {}
        self.entity = {}  # always empty when forbid_entities (every decl is blocked)

        # --- tree-building glue (mirrors stdlib xml.etree XMLParser) ---
        # Guard the optional target callbacks with hasattr, like the stdlib, so a
        # custom target providing only the core protocol (start/end/data/close)
        # works (a default TreeBuilder has all of these).
        parser.DefaultHandlerExpand = self._default
        if hasattr(self.target, "start"):
            parser.StartElementHandler = self._start
        if hasattr(self.target, "end"):
            parser.EndElementHandler = self._end
        if hasattr(self.target, "data"):
            parser.CharacterDataHandler = self.target.data
        if hasattr(self.target, "comment"):
            parser.CommentHandler = self.target.comment
        if hasattr(self.target, "pi"):
            parser.ProcessingInstructionHandler = self.target.pi
        parser.buffer_text = 1
        parser.ordered_attributes = 1

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
        attrib = {}
        if attr_list:
            for i in range(0, len(attr_list), 2):
                attrib[fixname(attr_list[i])] = attr_list[i + 1]
        return self.target.start(tag, attrib)

    def _end(self, tag):
        return self.target.end(self._fixname(tag))

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

                def handler(tag, attrib_in, event=event_name, append=append,
                            start=self._start):
                    append((event, start(tag, attrib_in)))
                parser.StartElementHandler = handler
            elif event_name == "end":
                def handler(tag, event=event_name, append=append, end=self._end):
                    append((event, end(tag)))
                parser.EndElementHandler = handler
            elif event_name == "start-ns":
                if hasattr(self.target, "start_ns"):
                    def handler(prefix, uri, event=event_name, append=append,
                                start_ns=self._start_ns):
                        append((event, start_ns(prefix, uri)))
                else:
                    def handler(prefix, uri, event=event_name, append=append):
                        append((event, (prefix or "", uri or "")))
                parser.StartNamespaceDeclHandler = handler
            elif event_name == "end-ns":
                if hasattr(self.target, "end_ns"):
                    def handler(prefix, event=event_name, append=append,
                                end_ns=self._end_ns):
                        append((event, end_ns(prefix)))
                else:
                    def handler(prefix, event=event_name, append=append):
                        append((event, None))
                parser.EndNamespaceDeclHandler = handler
            elif event_name == "comment":
                def handler(text, event=event_name, append=append, self=self):
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
    def feed(self, data):
        try:
            self.parser.Parse(data, False)
        except self._error as v:
            self._cleanup()
            self._raiseerror(v)
        except BaseException:
            # blocking refusals (EntitiesForbidden/...) and anything else
            self._cleanup()
            raise

    def close(self):
        try:
            try:
                self.parser.Parse(b"", True)
            except self._error as v:
                self._raiseerror(v)
            return self.target.close()
        finally:
            self._cleanup()


def fromstring(text, forbid_dtd=False, forbid_entities=True, forbid_external=True):
    """Parse XML *text* into an ``xml.etree.ElementTree.Element``, safely.

    Behaviorally equivalent to ``defusedxml.ElementTree.fromstring``: entity
    declarations and external reference resolution are blocked (raising
    ``EntitiesForbidden`` / ``ExternalReferenceForbidden``, both ``ValueError``
    subclasses); ``forbid_dtd=True`` additionally blocks any DOCTYPE
    (``DTDForbidden``); malformed input raises ``xml.etree.ElementTree.ParseError``.
    Stdlib-only.
    """
    parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                       forbid_external=forbid_external)
    parser.feed(text)
    return parser.close()


def parse(source, parser=None, forbid_dtd=False, forbid_entities=True,
          forbid_external=True):
    """Parse XML from *source* (a filename or file-like) into a hardened
    ``ElementTree``. Mirrors ``defusedxml.ElementTree.parse``."""
    if parser is None:
        parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                           forbid_external=forbid_external)
    return _stdlib_parse(source, parser)


def fromstringlist(sequence, parser=None, forbid_dtd=False, forbid_entities=True,
                   forbid_external=True):
    """Parse a *sequence* of XML string fragments into an ``Element``, safely.

    Stdlib-parity addition (``defusedxml.ElementTree`` does not provide
    ``fromstringlist``); behaves like a hardened ``xml.etree.ElementTree``
    ``fromstringlist`` — equivalent to ``fromstring("".join(sequence))``.
    """
    if parser is None:
        parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                           forbid_external=forbid_external)
    for text in sequence:
        parser.feed(text)
    return parser.close()


def iterparse(source, events=None, parser=None, forbid_dtd=False,
              forbid_entities=True, forbid_external=True):
    """Incrementally parse XML from *source*, yielding ``(event, elem)`` pairs, safely.

    Mirrors ``defusedxml.ElementTree.iterparse``. Reuses the stdlib `iterparse`
    iterator driving purexml's hardened `XMLParser` via `_setevents` — so the
    blocking handlers fire *during* the incremental feed (bombs/XXE are blocked at
    the declaration mid-stream, before the consumer iterates past them), and the
    parser's error/close cleanup releases the heavy state. Default events: `"end"`.
    """
    if parser is None:
        parser = XMLParser(forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
                           forbid_external=forbid_external)
    return _stdlib_iterparse(source, events, parser)
