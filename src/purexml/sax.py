"""``purexml.sax`` — a hardened drop-in for ``defusedxml.sax``.

Event-driven, not a tree: `make_parser()` returns a hardened `XMLReader` and
`parse()` / `parseString()` drive it with a caller-supplied `ContentHandler`, whose
`startElement` / `characters` / `endElement` / … callbacks fire as the document streams.
Same signature + defaults as ``defusedxml.sax``; the hardening rides on
``purexml.expatreader``. Malformed input surfaces as the stdlib ``SAXParseException`` via the
``ErrorHandler`` (equivalent to the oracle), **not** a ``PureXMLError``. Stdlib-only; zero-dep.

`parseString` takes **bytes** (mirroring ``defusedxml.sax`` exactly — it wraps the input in a
``BytesIO``; a ``str`` raises ``TypeError`` on both, so purexml does not over-accept beyond the
oracle).
"""
from __future__ import annotations

from io import BytesIO
from typing import Any
from xml.sax import ErrorHandler as _ErrorHandler
from xml.sax import InputSource as _InputSource
from xml.sax.handler import ContentHandler

from . import expatreader as _expatreader

__all__ = ["make_parser", "parse", "parseString"]


def make_parser(parser_list: Any = []) -> _expatreader._DefusedExpatParser:  # noqa: B006
    """Return a hardened SAX `XMLReader`. ``parser_list`` is accepted for signature
    compatibility and ignored — like ``defusedxml.sax``, this always returns its own
    hardened reader (a foreign driver would bypass purexml's blocking)."""
    return _expatreader.create_parser()


def parse(source: Any, handler: ContentHandler, errorHandler: Any = _ErrorHandler(),
          forbid_dtd: bool = False, forbid_entities: bool = True,
          forbid_external: bool = True) -> None:
    """Parse *source* (filename / URL / open stream / `InputSource`) with the hardened reader,
    driving *handler*. Same signature/defaults as ``defusedxml.sax.parse``."""
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.forbid_dtd = forbid_dtd
    parser.forbid_entities = forbid_entities
    parser.forbid_external = forbid_external
    parser.parse(source)


def parseString(string: bytes, handler: ContentHandler, errorHandler: Any = _ErrorHandler(),
                forbid_dtd: bool = False, forbid_entities: bool = True,
                forbid_external: bool = True) -> None:
    """Parse a **bytes** document with the hardened reader, driving *handler*. Same
    signature/defaults as ``defusedxml.sax.parseString`` (bytes-only — see module docstring)."""
    if errorHandler is None:
        errorHandler = _ErrorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.forbid_dtd = forbid_dtd
    parser.forbid_entities = forbid_entities
    parser.forbid_external = forbid_external
    inpsrc = _InputSource()
    inpsrc.setByteStream(BytesIO(string))
    parser.parse(inpsrc)
