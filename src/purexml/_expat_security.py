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

#: Functional floor: 2.6.0 covers billion-laughs (since 2.4.0) AND the large-tokens
#: / CVE-2023-52425 reparse-deferral mitigation (2.6.0). The major DoS classes are
#: mitigated here, but the *disproportionate dynamic memory* class stays live below
#: RECOMMENDED. Opt into this looser bar explicitly. Provisional.
SAFE_EXPAT_VERSION = (2, 6, 0)

#: Conservative floor named by current CPython docs (``xml`` security section):
#: Expat < 2.7.2 "may be vulnerable" to several classes. **The default** for the
#: secure checks below — fail-safe (under-reporting security is worse than
#: over-reporting). Provisional; the precise floor + enforce-vs-warn policy is a
#: 1.0-freeze decision.
RECOMMENDED_EXPAT_VERSION = (2, 7, 2)


def _as_version_tuple(v):
    """Normalize a version to a tuple of ints. Accepts a ``"x.y.z"`` string or a
    sequence of ints, so callers can pass either form (PR#3 Gemini)."""
    if isinstance(v, str):
        return tuple(int(p) for p in v.split("."))
    return tuple(int(p) for p in v)


def expat_is_secure(minimum=RECOMMENDED_EXPAT_VERSION):
    """Return ``True`` if the runtime libexpat meets *minimum*.

    Defaults to the **conservative** floor (`RECOMMENDED_EXPAT_VERSION`, fail-safe).
    Pass `SAFE_EXPAT_VERSION` for the looser functional bar, or any
    ``(maj, min, micro)`` tuple / ``"x.y.z"`` string. Opt-in — purexml does not
    enforce this automatically.
    """
    return EXPAT_VERSION >= _as_version_tuple(minimum)


def assert_expat_secure(minimum=RECOMMENDED_EXPAT_VERSION):
    """Raise ``RuntimeError`` if the runtime libexpat is below *minimum* (default
    the conservative `RECOMMENDED_EXPAT_VERSION`).

    For consumers that want to fail-closed on an unsafe runtime. Not called
    automatically; the enforce-vs-warn policy is deferred to the 1.0 freeze.
    """
    floor = _as_version_tuple(minimum)
    if EXPAT_VERSION < floor:
        cur = ".".join(map(str, EXPAT_VERSION))
        need = ".".join(map(str, floor))
        raise RuntimeError(
            "libexpat %s is below purexml's safe floor %s — the runtime may be "
            "vulnerable to XML DoS classes mitigated only at the expat layer "
            "(billion laughs, quadratic blowup, large tokens / CVE-2023-52425, "
            "disproportionate dynamic memory). Upgrade Python or the system expat."
            % (cur, need)
        )
