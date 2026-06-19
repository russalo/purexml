"""``purexml.common`` — the defusedxml exception-compatibility surface.

This module exists for one reason: to make ``s/defusedxml/purexml/`` work at *catch
sites* across every purexml module. Code that catches the defusedxml base exception::

    >>> from defusedxml.common import DefusedXmlException   # before
    >>> from purexml.common import DefusedXmlException      # after s/defusedxml/purexml/
    >>> # ... except DefusedXmlException: ...

migrates verbatim — because purexml's
own block exceptions (`EntitiesForbidden` / `ExternalReferenceForbidden` / `DTDForbidden` /
`NotSupportedError`) already carry defusedxml's names, and the only base-name difference
(`DefusedXmlException` vs `PureXMLError`) is bridged by the alias below. Both bases are
``ValueError`` subclasses with the same MRO position, so ``except DefusedXmlException``
catches a purexml refusal exactly as it caught a defusedxml one.

This is a **compatibility layer**: the defusedxml name lives here only. The top-level
``purexml`` namespace stays purexml-native (`PureXMLError`).
"""
from __future__ import annotations

from .errors import (
    DTDForbidden,
    EntitiesForbidden,
    ExternalReferenceForbidden,
    NotSupportedError,
    PureXMLError,
)

#: Alias for defusedxml's base exception name. ``PureXMLError`` *is* purexml's base
#: refusal (a ``ValueError``); exposing it under defusedxml's name lets ``except
#: DefusedXmlException`` survive the migration unchanged.
DefusedXmlException = PureXMLError

__all__ = [
    "DefusedXmlException",
    "DTDForbidden",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
    "NotSupportedError",
]
