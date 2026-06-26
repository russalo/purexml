"""``purexml.expatreader`` — a hardened SAX driver for pyexpat.

The engine behind ``purexml.sax`` (and the drop-in for ``defusedxml.expatreader``): a subclass
of stdlib ``xml.sax.expatreader.ExpatParser`` that installs purexml's blocking handlers on the
expat parser **in ``reset()``** — exactly where the stdlib reader (re)creates ``self._parser``.
The handlers raise *purexml's* exceptions, mapping expat's callback args to purexml's
constructors exactly as ``_parser.py`` / ``minidom.py`` do (purexml's signatures differ from
defusedxml's). Stdlib-only (``xml.sax`` is under the ``xml`` package) — no third-party dependency.
"""
from __future__ import annotations

from typing import Any
from xml.sax.expatreader import ExpatParser as _ExpatParser

from .errors import DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden

__all__ = ["DefusedExpatParser", "create_parser"]


class DefusedExpatParser(_ExpatParser):
    """Stdlib ``ExpatParser`` + purexml's blocking handlers — the mirror of
    ``defusedxml.expatreader.DefusedExpatParser``, raising purexml's exceptions."""

    def __init__(self, namespaceHandling: int = 0, bufsize: int = 2 ** 16 - 20,
                 forbid_dtd: bool = False, forbid_entities: bool = True,
                 forbid_external: bool = True) -> None:
        # namespaceHandling stays `int` to match defusedxml's signature (typeshed narrows the
        # base param to Literal[0,1]|bool; 0/1 are the real values).
        super().__init__(namespaceHandling, bufsize)  # type: ignore[arg-type]
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        self.forbid_external = forbid_external

    # Blocking handlers — arg mapping matches `_parser.py` (purexml's exception signatures).
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

    def reset(self) -> None:
        super().reset()
        parser: Any = self._parser  # stdlib (re)creates the expat parser here
        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self._forbid_dtd
        if self.forbid_entities:
            parser.EntityDeclHandler = self._forbid_entity_decl
            parser.UnparsedEntityDeclHandler = self._forbid_unparsed_entity_decl
        if self.forbid_external:
            parser.ExternalEntityRefHandler = self._forbid_external_ref

    def parse(self, source: Any) -> None:
        # The stdlib ExpatParser clears self._parser only on the SUCCESS path (close()); on a
        # malformed/blocked parse it raises first, so clear the reader->parser edge on EVERY path
        # (the minidom PR#28 hygiene). NOTE: unlike ElementTree/minidom this does NOT make the SAX
        # reader fully refcount-reclaimable — a residual cycle lives in pyexpat's exception
        # retention (a C-level cycle unreachable from Python; defusedxml.sax has it too). It is
        # reclaimed by cyclic GC (no leak), which the regression test asserts. No event-stream change.
        try:
            super().parse(source)
        finally:
            self._parser = None


def create_parser(*args: Any, **kwargs: Any) -> DefusedExpatParser:
    """Return a hardened SAX `XMLReader` (mirror of `defusedxml.expatreader.create_parser`)."""
    return DefusedExpatParser(*args, **kwargs)
