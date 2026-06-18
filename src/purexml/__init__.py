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
    BLOCKED,
    EXPAT_MITIGATED,
    EXPAT_VERSION,
    LIVE,
    OPT_IN,
    RECOMMENDED_EXPAT_VERSION,
    SAFE_EXPAT_VERSION,
    SecurityReport,
    assert_expat_secure,
    expat_is_secure,
    security_report,
)
from ._parser import XMLParser, fromstring, fromstringlist, iterparse, parse
from .errors import (
    AttributesExceeded,
    DepthExceeded,
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    LimitExceeded,
    PureXMLError,
    SizeExceeded,
)
from .limits import RECOMMENDED_LIMITS, Limits

XML = fromstring

__version__ = "0.8.0"

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
    # opt-in structural-DoS limits (v0.4 mirror-plus)
    "Limits",
    "RECOMMENDED_LIMITS",
    "LimitExceeded",
    "DepthExceeded",
    "AttributesExceeded",
    "SizeExceeded",
    # libexpat version awareness (v0.1.2) — opt-in
    "EXPAT_VERSION",
    "SAFE_EXPAT_VERSION",
    "RECOMMENDED_EXPAT_VERSION",
    "expat_is_secure",
    "assert_expat_secure",
    # security-posture report (v0.5 trust surface) — read-only introspection
    "security_report",
    "SecurityReport",
    "BLOCKED",
    "EXPAT_MITIGATED",
    "OPT_IN",
    "LIVE",
    "__version__",
]
