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
                 forbid_entities: bool = True, forbid_external: bool = True) -> None:
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


def _builder(forbid_dtd: bool, forbid_entities: bool,
             forbid_external: bool) -> _DefusedExpatBuilder:
    # Namespace-aware by default, matching stdlib/defusedxml minidom.
    return _DefusedExpatBuilderNS(
        forbid_dtd=forbid_dtd, forbid_entities=forbid_entities,
        forbid_external=forbid_external)


def parse(file: str | IO[Any], parser: Any = None, bufsize: int | None = None,
          forbid_dtd: bool = False, forbid_entities: bool = True,
          forbid_external: bool = True) -> Document:
    """Parse a file (filename or open binary file object) into a hardened DOM ``Document``.

    Same signature/defaults as ``defusedxml.minidom.parse``. A caller-supplied ``parser``
    raises `NotSupportedError` (it would bypass hardening). ``bufsize`` is accepted for
    signature compatibility but does not change the hardened whole-document parse (the
    resulting ``Document`` is identical).
    """
    if parser is not None:
        raise NotSupportedError(_CUSTOM_PARSER_MSG)
    builder = _builder(forbid_dtd, forbid_entities, forbid_external)
    if isinstance(file, str):
        with open(file, "rb") as fp:
            return builder.parseFile(fp)
    return builder.parseFile(file)


def parseString(string: str | bytes, parser: Any = None, forbid_dtd: bool = False,
                forbid_entities: bool = True,
                forbid_external: bool = True) -> Document:
    """Parse a string/bytes into a hardened DOM ``Document``.

    Same signature/defaults as ``defusedxml.minidom.parseString``. A caller-supplied
    ``parser`` raises `NotSupportedError`.
    """
    if parser is not None:
        raise NotSupportedError(_CUSTOM_PARSER_MSG)
    builder = _builder(forbid_dtd, forbid_entities, forbid_external)
    return builder.parseString(string)
