"""purexml exception hierarchy.

Blocked-input refusals subclass ``ValueError`` — mirroring defusedxml's
``DefusedXmlException(ValueError)`` MRO (RFC §3.3 / measure-first F4) so that a
consumer narrowing to ``except ValueError`` stays behaviorally equivalent after
migrating off defusedxml. Malformed input is *not* one of these: it raises the
stdlib ``xml.etree.ElementTree.ParseError`` unchanged, exactly as the oracle does.
"""

__all__ = [
    "PureXMLError",
    "DTDForbidden",
    "EntitiesForbidden",
    "ExternalReferenceForbidden",
]


class PureXMLError(ValueError):
    """Base class for purexml security refusals (a ``ValueError`` subclass)."""


class DTDForbidden(PureXMLError):
    """A DOCTYPE / DTD was encountered while ``forbid_dtd=True``.

    Off by default (defusedxml's default is ``forbid_dtd=False`` — an entity-free
    DTD is allowed), so this fires only when a caller opts into the stricter
    DTD-disabling mode (OWASP's strongest XXE/DoS control). Mirrors defusedxml's
    ``DTDForbidden``.
    """

    def __init__(self, name, sysid=None, pubid=None):
        super().__init__(
            "DTDForbidden(name=%r, system_id=%r, public_id=%r)" % (name, sysid, pubid)
        )
        self.name = name
        self.sysid = sysid
        self.pubid = pubid


class EntitiesForbidden(PureXMLError):
    """An entity *declaration* was encountered (general or parameter).

    Blocked at declaration time, before any expansion or resolution — this is the
    billion-laughs / quadratic-blowup / declared-XXE defense (defusedxml's
    ``forbid_entities``).
    """

    def __init__(self, name, sysid=None, pubid=None):
        super().__init__(
            "EntitiesForbidden(name=%r, system_id=%r, public_id=%r)"
            % (name, sysid, pubid)
        )
        self.name = name
        self.sysid = sysid
        self.pubid = pubid


class ExternalReferenceForbidden(PureXMLError):
    """Resolution of an external reference was attempted (defusedxml's
    ``forbid_external``). The backstop for external resolution paths that do not
    pass through a forbidden entity declaration.
    """

    def __init__(self, sysid=None, pubid=None):
        super().__init__(
            "ExternalReferenceForbidden(system_id=%r, public_id=%r)" % (sysid, pubid)
        )
        self.sysid = sysid
        self.pubid = pubid
