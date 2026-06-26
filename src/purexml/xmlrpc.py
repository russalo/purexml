"""``purexml.xmlrpc`` — a hardened drop-in for ``defusedxml.xmlrpc``.

Unlike the parse-surface modules this is a **monkeypatch shim**: ``monkey_patch()`` makes the
stdlib ``xmlrpc.client`` safe — a defused expat parser (entity/DTD/external blocking) plus a
bounded gzip decode (anti-decompression-bomb, ``MAX_DATA``). Mirrors ``defusedxml.xmlrpc``.

**Option C — lazy imports (the no-I/O-at-import guarantee, RFC v0.13 §2/§4):** every ``xmlrpc`` /
``gzip`` / ``io`` import happens INSIDE ``monkey_patch()`` and the gzip helpers, never at module
top. So ``import purexml`` (and ``import purexml.xmlrpc``) never pulls ``xmlrpc.client`` /
``socket`` / ``http`` / ``gzip`` — the network-capable import enters only when a consumer
*explicitly* calls ``monkey_patch()``. purexml never imports the transport itself (``socket`` /
``http`` stay forbidden in the no-I/O guard even here; the network reach is ``xmlrpc.client``'s).
"""
from __future__ import annotations

from typing import Any

from .errors import DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden

__all__ = ["monkey_patch", "unmonkey_patch", "defused_gzip_decode", "MAX_DATA"]

#: Cap on gzip-decoded size — bounds decompression bombs (mirrors defusedxml's 30 MB).
MAX_DATA = 30 * 1024 * 1024

# Lazily-built caches (option C: nothing network-capable imported at module top).
_defused_parser_cls: Any = None
_orig_fast_parser: Any = None
_orig_gzip_decode: Any = None
_orig_gzip_response: Any = None
_patched = False


def _build_defused_parser_cls() -> Any:
    """Lazily import ``xmlrpc.client`` and define the defused ``ExpatParser`` subclass (cached).
    Can't be a module-level class — that would import the transport at import time."""
    global _defused_parser_cls
    if _defused_parser_cls is not None:
        return _defused_parser_cls
    from xmlrpc.client import ExpatParser as _ExpatParser

    class DefusedExpatParser(_ExpatParser):
        """``xmlrpc.client.ExpatParser`` + purexml's blocking handlers (arg-mapped to
        purexml's exception signatures, as in ``_parser.py``)."""

        def __init__(self, target: Any, forbid_dtd: bool = False,
                     forbid_entities: bool = True, forbid_external: bool = True) -> None:
            super().__init__(target)
            self.forbid_dtd = forbid_dtd
            self.forbid_entities = forbid_entities
            self.forbid_external = forbid_external
            parser = self._parser  # type: ignore[attr-defined]
            if forbid_dtd:
                parser.StartDoctypeDeclHandler = self._forbid_dtd
            if forbid_entities:
                parser.EntityDeclHandler = self._forbid_entity_decl
                parser.UnparsedEntityDeclHandler = self._forbid_unparsed_entity_decl
            if forbid_external:
                parser.ExternalEntityRefHandler = self._forbid_external_ref

        def _forbid_dtd(self, name: str, sysid: str | None, pubid: str | None,
                        has_internal_subset: int) -> None:
            raise DTDForbidden(name, sysid, pubid)

        def _forbid_entity_decl(self, name: str, is_parameter_entity: int, value: str | None,
                                base: str | None, sysid: str | None, pubid: str | None,
                                notation_name: str | None) -> None:
            raise EntitiesForbidden(name, sysid, pubid)

        def _forbid_unparsed_entity_decl(self, name: str, base: str | None, sysid: str | None,
                                         pubid: str | None, notation_name: str) -> None:
            raise EntitiesForbidden(name, sysid, pubid)

        def _forbid_external_ref(self, context: str, base: str | None, sysid: str | None,
                                 pubid: str | None) -> int:
            raise ExternalReferenceForbidden(sysid, pubid)

    _defused_parser_cls = DefusedExpatParser
    return DefusedExpatParser


def defused_gzip_decode(data: bytes, limit: int | None = None) -> bytes:
    """gzip-decode *data*, bounding the result to *limit* (default `MAX_DATA`) to stop
    decompression bombs. Mirrors ``defusedxml.xmlrpc.defused_gzip_decode``."""
    import gzip
    from io import BytesIO

    if limit is None:
        limit = MAX_DATA
    with BytesIO(data) as f, gzip.GzipFile(mode="rb", fileobj=f) as gzf:
        try:
            decoded = gzf.read() if limit < 0 else gzf.read(limit + 1)
        except OSError:
            # malformed gzip (incl. gzip.BadGzipFile, an OSError) -> ValueError, matching
            # defusedxml + the stdlib contract that xmlrpc's gzip_decode raises ValueError on
            # bad data (so SimpleXMLRPCRequestHandler returns 400 instead of letting it escape).
            raise ValueError("invalid data") from None
    if limit >= 0 and len(decoded) > limit:
        raise ValueError("max gzipped payload length exceeded")
    return decoded


def _build_gzip_response_cls() -> Any:
    """Lazily define the bounded ``GzipDecodedResponse`` subclass (anti-bomb)."""
    import gzip
    from io import BytesIO

    class DefusedGzipDecodedResponse(gzip.GzipFile):
        def __init__(self, response: Any, limit: int | None = None) -> None:
            self.limit = limit = MAX_DATA if limit is None else limit
            if limit < 0:
                data = response.read()
                self.readlength: int | None = None
            else:
                data = response.read(limit + 1)
                self.readlength = 0
            if limit >= 0 and len(data) > limit:
                raise ValueError("max payload length exceeded")
            self.stringio = BytesIO(data)
            super().__init__(mode="rb", fileobj=self.stringio)

        def read(self, n: int = -1) -> bytes:  # type: ignore[override]
            if self.limit >= 0:
                left = self.limit - (self.readlength or 0)
                # a negative n (the file-like default `read()`) would otherwise decompress the
                # WHOLE remaining stream into memory before the post-read check — a gzip bomb
                # could allocate past MAX_DATA before raising. Cap it to the limit. (PR#34.)
                n = left + 1 if n < 0 else min(n, left + 1)
                data = super().read(n)
                self.readlength = (self.readlength or 0) + len(data)
                if self.readlength > self.limit:
                    raise ValueError("max payload length exceeded")
                return data
            return super().read(n)

        def close(self) -> None:
            super().close()
            self.stringio.close()

    return DefusedGzipDecodedResponse


def monkey_patch() -> None:
    """Make the stdlib ``xmlrpc.client`` safe: install the defused parser (`FastParser`) + bounded
    gzip on ``xmlrpc.client`` (and ``xmlrpc.server``'s `gzip_decode`). Idempotent; reversible via
    `unmonkey_patch`. **This is the opt-in boundary where the `xmlrpc`/`gzip` import happens.**"""
    global _orig_fast_parser, _orig_gzip_decode, _orig_gzip_response, _patched
    from xmlrpc import client as xmlrpc_client
    try:
        from xmlrpc import server as xmlrpc_server
    except ImportError:  # pragma: no cover
        xmlrpc_server = None  # type: ignore[assignment]
    if not _patched:
        # Capture the ORIGINALS for a faithful undo (a prior patcher's FastParser is restored,
        # not clobbered to None). stdlib default FastParser is None — but capture, don't assume.
        _orig_fast_parser = getattr(xmlrpc_client, "FastParser", None)
        _orig_gzip_decode = getattr(xmlrpc_client, "gzip_decode", None)
        _orig_gzip_response = getattr(xmlrpc_client, "GzipDecodedResponse", None)
    # setattr (not direct assignment) so dynamically patching the stdlib module's typed
    # attributes stays mypy-clean — the idiomatic monkeypatch tool.
    setattr(xmlrpc_client, "FastParser", _build_defused_parser_cls())
    setattr(xmlrpc_client, "GzipDecodedResponse", _build_gzip_response_cls())
    setattr(xmlrpc_client, "gzip_decode", defused_gzip_decode)
    if xmlrpc_server is not None:
        setattr(xmlrpc_server, "gzip_decode", defused_gzip_decode)
    _patched = True


def unmonkey_patch() -> None:
    """Restore the stdlib ``xmlrpc`` to its original parser + gzip handling."""
    global _patched
    from xmlrpc import client as xmlrpc_client
    try:
        from xmlrpc import server as xmlrpc_server
    except ImportError:  # pragma: no cover
        xmlrpc_server = None  # type: ignore[assignment]
    setattr(xmlrpc_client, "FastParser", _orig_fast_parser)
    if _orig_gzip_response is not None:
        setattr(xmlrpc_client, "GzipDecodedResponse", _orig_gzip_response)
    if _orig_gzip_decode is not None:
        setattr(xmlrpc_client, "gzip_decode", _orig_gzip_decode)
        if xmlrpc_server is not None:
            setattr(xmlrpc_server, "gzip_decode", _orig_gzip_decode)
    _patched = False
