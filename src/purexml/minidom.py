"""``purexml.minidom`` — a hardened drop-in for ``defusedxml.minidom``.

Mirrors ``defusedxml.minidom``: ``parse`` / ``parseString`` return a standard
``xml.dom.minidom.Document`` with the same ``forbid_*`` signature and defaults. Hardening
is installed the way defusedxml does it — subclass the stdlib ``xml.dom.expatbuilder`` and
add blocking handlers to the underlying expat parser — **except** the handlers raise
*purexml's* exceptions, mapping expat's callback args to purexml's constructors exactly as
``_parser.py`` does (purexml's exception signatures differ from defusedxml's, so the handler
bodies map args; they are not copied verbatim).

Stdlib-only: ``xml.dom.minidom`` / ``xml.dom.expatbuilder`` live in the ``xml`` package, so
the no-I/O import guard holds and there is no third-party dependency. Returning a stdlib
``Document`` makes the result equivalent to the oracle by construction — we add blocking,
change nothing else.
"""
from __future__ import annotations

from typing import IO, Any
from xml.dom.expatbuilder import ExpatBuilder as _ExpatBuilder
from xml.dom.expatbuilder import Namespaces as _Namespaces
from xml.dom.minidom import Document

from .errors import (
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    NotSupportedError,
)
from .limits import Limits, _check_max_bytes, _counter_for

__all__ = ["parse", "parseString"]

_CUSTOM_PARSER_MSG = (
    "purexml.minidom supports only its own hardened parser; a caller-supplied `parser` "
    "is not accepted — a foreign parser would bypass purexml's entity/external/DTD "
    "blocking, which a security control must refuse rather than silently honor."
)


class _DefusedExpatBuilder(_ExpatBuilder):
    """Stdlib ``ExpatBuilder`` + purexml's blocking handlers — the mirror of
    ``defusedxml.expatbuilder.DefusedExpatBuilder``, raising purexml's exceptions."""

    def __init__(self, options: Any = None, forbid_dtd: bool = False,
                 forbid_entities: bool = True, forbid_external: bool = True,
                 limits: Limits | None = None) -> None:
        # opt-in structural-DoS accounting (v0.14); None == no depth/attr cap. MUST precede
        # super().__init__ — ExpatBuilder.__init__ calls self.reset(), which reads self._counter.
        self._counter = _counter_for(limits)
        super().__init__(options)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        self.forbid_external = forbid_external

    # Blocking handlers — arg mapping matches `_parser.py` (purexml's exception
    # signatures, NOT defusedxml's). Each refuses at declaration/resolution time.
    def _forbid_dtd(self, name: str, sysid: str | None, pubid: str | None,
                    has_internal_subset: int) -> None:
        raise DTDForbidden(name, sysid, pubid)

    def _forbid_entity_decl(self, name: str, is_parameter_entity: int,
                            value: str | None, base: str | None, sysid: str | None,
                            pubid: str | None, notation_name: str | None) -> None:
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_unparsed_entity_decl(self, name: str, base: str | None,
                                     sysid: str | None, pubid: str | None,
                                     notation_name: str) -> None:
        raise EntitiesForbidden(name, sysid, pubid)

    def _forbid_external_ref(self, context: str, base: str | None,
                             sysid: str | None, pubid: str | None) -> int:
        raise ExternalReferenceForbidden(sysid, pubid)

    def install(self, parser: Any) -> None:
        super().install(parser)
        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self._forbid_dtd
        if self.forbid_entities:
            parser.EntityDeclHandler = self._forbid_entity_decl
            parser.UnparsedEntityDeclHandler = self._forbid_unparsed_entity_decl
        if self.forbid_external:
            parser.ExternalEntityRefHandler = self._forbid_external_ref

    # The stdlib ExpatBuilder clears `self._parser` only on the SUCCESS path; a malformed
    # (or blocked) payload raises first, leaving the builder<->parser handler cycle to wait
    # for cyclic GC. Clear it on EVERY path so the builder is reclaimable by refcounting
    # alone — the same guarantee the ElementTree path makes (test_no_reference_cycle_after_parse;
    # PR#28 Codex). No parse-result change: the returned Document / raised exception is identical.
    def parseString(self, string: Any) -> Document:
        try:
            return super().parseString(string)
        finally:
            self._parser = None

    def parseFile(self, file: Any) -> Document:
        try:
            return super().parseFile(file)
        finally:
            self._parser = None


class _DefusedExpatBuilderNS(_Namespaces, _DefusedExpatBuilder):
    """Namespace-aware variant — mirror of ``defusedxml``'s ``DefusedExpatBuilderNS``."""

    def install(self, parser: Any) -> None:
        _DefusedExpatBuilder.install(self, parser)
        # `_options` / `_initNamespaces` are stdlib ExpatBuilder/Namespaces internals not
        # exposed in typeshed; this mirrors defusedxml's DefusedExpatBuilderNS verbatim.
        if self._options.namespace_declarations:  # type: ignore[attr-defined]
            parser.StartNamespaceDeclHandler = self.start_namespace_decl_handler

    def reset(self) -> None:
        _DefusedExpatBuilder.reset(self)
        self._initNamespaces()  # type: ignore[attr-defined]
        if self._counter is not None:
            self._counter.reset()

    # Depth/attr accounting (v0.14). These override `Namespaces`' element handlers (which win
    # in this class's MRO) and delegate to `super()`; minidom passes attributes as an ordered
    # LIST [name1, val1, ...], so the attribute count is len()//2. The root + all nested go
    # through `start_element_handler` (first_element_handler delegates to it), so this counts
    # every element.
    def start_element_handler(self, name: str, attributes: Any) -> None:
        if self._counter is not None:
            self._counter.enter(name, len(attributes) // 2)
        super().start_element_handler(name, attributes)

    def end_element_handler(self, name: str) -> None:
        if self._counter is not None:
            self._counter.leave()
        super().end_element_handler(name)


def _builder(forbid_dtd: bool, forbid_entities: bool, forbid_external: bool,
             limits: Limits | None = None) -> _DefusedExpatBuilder:
    # Namespace-aware by default, matching stdlib/defusedxml minidom.
    return _DefusedExpatBuilderNS(
        forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
        forbid_external=forbid_external, limits=limits)


def parse(file: str | IO[Any], parser: Any = None, bufsize: int | None = None,
          forbid_dtd: bool = False, forbid_entities: bool = True,
          forbid_external: bool = True, *, limits: Limits | None = None) -> Document:
    """Parse a file (filename or open binary file object) into a hardened DOM ``Document``.

    Same signature/defaults as ``defusedxml.minidom.parse`` (a caller-supplied ``parser``
    raises `NotSupportedError`; ``bufsize`` is accepted for compat but doesn't change the
    result). The keyword-only ``limits`` (purexml's opt-in structural-DoS caps) enforces
    ``max_depth`` / ``max_attributes`` here; ``max_bytes`` is enforced on `parseString` only
    (a stream's length isn't known up front) — default ``None`` is a no-op (mirror unchanged).
    """
    if parser is not None:
        raise NotSupportedError(_CUSTOM_PARSER_MSG)
    builder = _builder(forbid_dtd, forbid_entities, forbid_external, limits)
    if isinstance(file, str):
        with open(file, "rb") as fp:
            return builder.parseFile(fp)
    return builder.parseFile(file)


def parseString(string: str | bytes, parser: Any = None, forbid_dtd: bool = False,
                forbid_entities: bool = True, forbid_external: bool = True,
                *, limits: Limits | None = None) -> Document:
    """Parse a string/bytes into a hardened DOM ``Document``.

    Same signature/defaults as ``defusedxml.minidom.parseString`` (a caller-supplied ``parser``
    raises `NotSupportedError`). The keyword-only ``limits`` enforces all three opt-in caps
    (``max_depth`` / ``max_attributes`` / ``max_bytes``); default ``None`` is a no-op (mirror).
    """
    if parser is not None:
        raise NotSupportedError(_CUSTOM_PARSER_MSG)
    _check_max_bytes(string, limits)
    builder = _builder(forbid_dtd, forbid_entities, forbid_external, limits)
    return builder.parseString(string)
