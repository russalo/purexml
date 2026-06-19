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
    "NotSupportedError",
    "LimitExceeded",
    "DepthExceeded",
    "AttributesExceeded",
    "SizeExceeded",
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

    def __init__(self, name: str, sysid: str | None = None,
                 pubid: str | None = None) -> None:
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

    def __init__(self, name: str, sysid: str | None = None,
                 pubid: str | None = None) -> None:
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

    def __init__(self, sysid: str | None = None, pubid: str | None = None) -> None:
        super().__init__(
            "ExternalReferenceForbidden(system_id=%r, public_id=%r)" % (sysid, pubid)
        )
        self.sysid = sysid
        self.pubid = pubid


class NotSupportedError(PureXMLError):
    """A requested operation is not supported by purexml (mirrors defusedxml's
    ``NotSupportedError``). Raised, e.g., when `purexml.minidom.parse` is handed a
    caller-supplied ``parser`` — a foreign parser would bypass purexml's hardening, so a
    security control refuses it rather than honor it unhardened.
    """


class LimitExceeded(PureXMLError):
    """Base for opt-in structural-DoS limit breaches (v0.4 mirror-plus).

    These fire only when a caller passes `limits=` — defusedxml has no caps, so by
    default purexml does not raise these (the strict-mirror default is preserved).
    """


class DepthExceeded(LimitExceeded):
    """Element nesting deeper than `limits.max_depth`."""

    def __init__(self, depth: int, limit: int) -> None:
        super().__init__("DepthExceeded(depth=%d, max_depth=%d)" % (depth, limit))
        self.depth = depth
        self.limit = limit


class AttributesExceeded(LimitExceeded):
    """An element with more attributes than `limits.max_attributes`."""

    def __init__(self, tag: str, count: int, limit: int) -> None:
        super().__init__(
            "AttributesExceeded(element=%r, count=%d, max_attributes=%d)"
            % (tag, count, limit)
        )
        self.tag = tag
        self.count = count
        self.limit = limit


class SizeExceeded(LimitExceeded):
    """Total input fed exceeds `limits.max_bytes`."""

    def __init__(self, size: int, limit: int) -> None:
        super().__init__("SizeExceeded(bytes=%d, max_bytes=%d)" % (size, limit))
        self.size = size
        self.limit = limit
