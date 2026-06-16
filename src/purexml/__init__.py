"""purexml — safely parse untrusted XML using only the Python standard library.

Drop-in replacement for ``defusedxml.ElementTree.fromstring``: returns a standard
``xml.etree.ElementTree.Element`` while blocking the known XML attack classes
(entity-expansion bombs, XXE, external reference resolution), behaviorally
equivalent to defusedxml's default configuration. Zero runtime dependencies.

    >>> from purexml import fromstring
    >>> root = fromstring("<r><a>x</a></r>")   # raises on bomb / XXE / malformed
"""

from xml.etree.ElementTree import ParseError

from ._expat_security import (
    EXPAT_VERSION,
    RECOMMENDED_EXPAT_VERSION,
    SAFE_EXPAT_VERSION,
    assert_expat_secure,
    expat_is_secure,
)
from ._parser import fromstring
from .errors import EntitiesForbidden, ExternalReferenceForbidden, PureXMLError

__version__ = "0.1.2"

__all__ = [
    "fromstring",
    "PureXMLError",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
    "ParseError",
    # libexpat version awareness (v0.1.2) — opt-in; see _expat_security
    "EXPAT_VERSION",
    "SAFE_EXPAT_VERSION",
    "RECOMMENDED_EXPAT_VERSION",
    "expat_is_secure",
    "assert_expat_secure",
    "__version__",
]
