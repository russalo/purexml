"""libexpat version awareness — purexml's value-add over (abandoned) defusedxml.

Resource-bound protection against XML DoS — billion-laughs, quadratic blowup,
large-tokens (CVE-2023-52425), disproportionate dynamic memory — lives in
**libexpat**, not the Python wrapper, so it depends entirely on the bundled/system
expat version. defusedxml (frozen 2021) never checked this; purexml exposes it so
a consumer can verify its runtime is actually safe.

Floor is **provisional** (it moves as expat ships fixes: 2.4.0 billion-laughs cap,
2.6.0 reparse-deferral / large-tokens, 2.7.2 per current CPython docs). The
enforce-vs-warn *policy* is a 1.0-freeze decision; v0.1.x only exposes the data +
an explicit opt-in check, with **no import-time behavior change.**
"""
import xml.parsers.expat as _expat

__all__ = [
    "EXPAT_VERSION",
    "SAFE_EXPAT_VERSION",
    "RECOMMENDED_EXPAT_VERSION",
    "expat_is_secure",
    "assert_expat_secure",
]

#: Runtime libexpat version as a ``(major, minor, micro)`` tuple.
EXPAT_VERSION = _expat.version_info

#: Functional safe floor: 2.6.0 covers billion-laughs (since 2.4.0) AND the
#: large-tokens / CVE-2023-52425 reparse-deferral mitigation (2.6.0). Provisional.
SAFE_EXPAT_VERSION = (2, 6, 0)

#: Conservative floor named by current CPython docs (``xml`` security section).
RECOMMENDED_EXPAT_VERSION = (2, 7, 2)


def expat_is_secure(minimum=SAFE_EXPAT_VERSION):
    """Return ``True`` if the runtime libexpat meets *minimum* (default the
    functional safe floor). Opt-in — purexml does not enforce this automatically."""
    return EXPAT_VERSION >= tuple(minimum)


def assert_expat_secure(minimum=SAFE_EXPAT_VERSION):
    """Raise ``RuntimeError`` if the runtime libexpat is below *minimum*.

    For consumers that want to fail-closed on an unsafe runtime. Not called
    automatically; the enforce-vs-warn policy is deferred to the 1.0 freeze.
    """
    if not expat_is_secure(minimum):
        cur = ".".join(map(str, EXPAT_VERSION))
        need = ".".join(map(str, minimum))
        raise RuntimeError(
            "libexpat %s is below purexml's safe floor %s — the runtime may be "
            "vulnerable to XML DoS classes mitigated only at the expat layer "
            "(billion laughs, quadratic blowup, large tokens / CVE-2023-52425). "
            "Upgrade Python or the system expat." % (cur, need)
        )
