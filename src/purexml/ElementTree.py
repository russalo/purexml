"""purexml.ElementTree — canonical namespace mirroring ``defusedxml.ElementTree``.

The migration off defusedxml is a literal ``s/defusedxml/purexml/`` for the
implemented surface::

    # was: from defusedxml.ElementTree import fromstring, parse, XML, XMLParser
    from purexml.ElementTree import fromstring, parse, XML, XMLParser

**Scope honesty:** this mirrors defusedxml.ElementTree's *shape* for the surface
purexml implements. Names purexml hasn't shipped yet (notably ``iterparse``, which
arrives in v0.3) are simply absent — accessing one raises ``AttributeError``, a
loud immediate failure, never a silent wrong-parse.

``ParseError`` and ``tostring`` are re-exported from the stdlib exactly as
defusedxml does. ``Element`` is intentionally NOT re-exported (defusedxml doesn't
either); import it from ``xml.etree.ElementTree`` if needed. ``fromstringlist`` is
a stdlib-parity extra beyond defusedxml's surface.
"""
from xml.etree.ElementTree import ParseError, tostring

from ._parser import XMLParser, fromstring, fromstringlist, parse
from .errors import (
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    PureXMLError,
)

#: ``XML`` is defusedxml's/stdlib's alias for ``fromstring``.
XML = fromstring

#: defusedxml back-compat aliases for the parser class.
XMLParse = XMLTreeBuilder = XMLParser

__all__ = [
    # mirrors defusedxml.ElementTree's __all__ (for the implemented surface)
    "ParseError",
    "XML",
    "XMLParse",
    "XMLParser",
    "XMLTreeBuilder",
    "fromstring",
    "parse",
    "tostring",
    # stdlib-parity extra (not in defusedxml)
    "fromstringlist",
    # purexml exception hierarchy
    "PureXMLError",
    "DTDForbidden",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
]
