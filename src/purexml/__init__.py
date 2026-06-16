"""purexml — safely parse untrusted XML using only the Python standard library.

Drop-in replacement for ``defusedxml.ElementTree.fromstring``: returns a standard
``xml.etree.ElementTree.Element`` while blocking the known XML attack classes
(entity-expansion bombs, XXE, external reference resolution), behaviorally
equivalent to defusedxml's default configuration. Zero runtime dependencies.

    >>> from purexml import fromstring
    >>> root = fromstring("<r><a>x</a></r>")   # raises on bomb / XXE / malformed
"""

from xml.etree.ElementTree import ParseError

from ._parser import fromstring
from .errors import EntitiesForbidden, ExternalReferenceForbidden, PureXMLError

__version__ = "0.1.1"

__all__ = [
    "fromstring",
    "PureXMLError",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
    "ParseError",
    "__version__",
]
