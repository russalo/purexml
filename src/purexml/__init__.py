"""purexml — safely parse untrusted XML using only the Python standard library.

A maintained, zero-dependency, stdlib-only replacement for ``defusedxml``: returns
standard ``xml.etree`` objects while blocking the known XML attack classes
(entity-expansion bombs, XXE, external reference resolution), behaviorally
equivalent to defusedxml's defaults.

The canonical namespace mirrors ``defusedxml.ElementTree`` (migration is a literal
``s/defusedxml/purexml/``)::

    from purexml.ElementTree import fromstring, parse, XML, XMLParser

The common entry points are also re-exported at the top level for convenience::

    from purexml import fromstring
    root = fromstring("<r><a>x</a></r>")   # raises on bomb / XXE / malformed
"""
from xml.etree.ElementTree import ParseError, tostring

from . import ElementTree
from ._expat_security import (
    EXPAT_VERSION,
    RECOMMENDED_EXPAT_VERSION,
    SAFE_EXPAT_VERSION,
    assert_expat_secure,
    expat_is_secure,
)
from ._parser import XMLParser, fromstring, fromstringlist, iterparse, parse
from .errors import (
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    PureXMLError,
)

XML = fromstring

__version__ = "0.3.0"

__all__ = [
    # the ElementTree family (also at purexml.ElementTree)
    "ElementTree",
    "fromstring",
    "parse",
    "iterparse",
    "fromstringlist",
    "XML",
    "XMLParser",
    "tostring",
    "ParseError",
    # exception hierarchy
    "PureXMLError",
    "DTDForbidden",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
    # libexpat version awareness (v0.1.2) — opt-in
    "EXPAT_VERSION",
    "SAFE_EXPAT_VERSION",
    "RECOMMENDED_EXPAT_VERSION",
    "expat_is_secure",
    "assert_expat_secure",
    "__version__",
]
