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
from collections import namedtuple
from types import MappingProxyType

from .limits import RECOMMENDED_LIMITS

__all__ = [
    "EXPAT_VERSION",
    "SAFE_EXPAT_VERSION",
    "RECOMMENDED_EXPAT_VERSION",
    "expat_is_secure",
    "assert_expat_secure",
    "security_report",
    "SecurityReport",
    "BLOCKED",
    "EXPAT_MITIGATED",
    "OPT_IN",
    "LIVE",
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


# -- v0.5 trust surface: the security-posture report ------------------------
#
# Per-class mitigation *status* values. Each attack class in a SecurityReport's
# ``mitigations`` map carries exactly one of these, answering "where, on THIS
# runtime, is this class handled?" They are plain strings (printable, stable to
# compare) — an adopter can branch on them without importing an enum type.

#: Blocked by purexml's own expat handlers, default-on — independent of libexpat
#: version (e.g. entity-decl refusal, external-ref refusal).
BLOCKED = "blocked-by-purexml"

#: Mitigated by the libexpat layer on this runtime (the runtime's expat version
#: is recent enough to cover the class). Not purexml's doing — reported so the
#: adopter knows the protection rides on the expat version.
EXPAT_MITIGATED = "mitigated-by-libexpat"

#: Covered only if the caller opts in (passes a ``Limits`` to the parse entry
#: point). Default-off — the strict defusedxml mirror does not bound this.
OPT_IN = "opt-in (pass Limits)"

#: NOT mitigated on this runtime: the class is real here and nothing covers it
#: (the libexpat version is below the floor that fixed it). An adopter should
#: upgrade expat and/or opt into the relevant control.
LIVE = "LIVE (not mitigated on this runtime)"


_ReportFields = [
    "expat_version",
    "expat_meets_safe_floor",
    "expat_meets_recommended",
    "recommended_limits",
    "mitigations",
    "notes",
]


class SecurityReport(namedtuple("SecurityReport", _ReportFields)):
    """The runtime's XML-security posture, as computed by `security_report`.

    A frozen, printable value object (a ``namedtuple`` subclass — typed fields +
    a readable ``__str__``). The tuple slots are read-only, and ``mitigations`` is
    a read-only mapping (``MappingProxyType``) so the whole report is genuinely
    immutable — appropriate for a trust surface an adopter logs and passes around.
    Fields:

    - ``expat_version`` — the runtime libexpat ``(maj, min, micro)`` tuple.
    - ``expat_meets_safe_floor`` — bool vs `SAFE_EXPAT_VERSION` (2.6.0).
    - ``expat_meets_recommended`` — bool vs `RECOMMENDED_EXPAT_VERSION` (2.7.2).
    - ``recommended_limits`` — the `RECOMMENDED_LIMITS` preset (opt-in caps).
    - ``mitigations`` — a mapping ``{attack_class: status}`` where status is one
      of `BLOCKED` / `EXPAT_MITIGATED` / `OPT_IN` / `LIVE`.
    - ``notes`` — a tuple of human-readable advisory strings (empty when the
      runtime is fully covered).

    **PROVISIONAL at 1.0** (per the ROADMAP freeze strategy): this is novel
    defense-in-depth over a moving libexpat landscape, so the report's shape and
    contents may evolve in a MINOR. The defusedxml-*mirror* surface is the frozen
    part; this introspection is not. Evolution rule for adopters: new fields are
    appended at the end — **access by attribute, not by position/index** — so a
    later field addition doesn't break you.
    """

    __slots__ = ()

    def __new__(cls, expat_version, expat_meets_safe_floor, expat_meets_recommended,
                recommended_limits, mitigations, notes):
        # Normalize the container fields so EVERY construction path — direct
        # construction AND ``_replace()`` — yields a genuinely immutable report,
        # not just ``security_report()``'s output (PR#8 Codex P2). ``mitigations``
        # becomes a defensive read-only view; ``notes`` a tuple.
        return super().__new__(
            cls, expat_version, expat_meets_safe_floor, expat_meets_recommended,
            recommended_limits, MappingProxyType(dict(mitigations)), tuple(notes))

    @classmethod
    def _make(cls, iterable):
        # Route _make (used by _replace) through __new__ so it normalizes too;
        # the default _make bypasses __new__ via tuple.__new__.
        return cls(*iterable)

    def __str__(self):
        ver = ".".join(map(str, self.expat_version))
        lines = [
            "purexml security posture",
            "  libexpat version: %s" % ver,
            "    meets safe floor (%s): %s"
            % (".".join(map(str, SAFE_EXPAT_VERSION)),
               "yes" if self.expat_meets_safe_floor else "NO"),
            "    meets recommended (%s): %s"
            % (".".join(map(str, RECOMMENDED_EXPAT_VERSION)),
               "yes" if self.expat_meets_recommended else "NO"),
            "  mitigations (where each attack class is handled on this runtime):",
        ]
        # default=0 guards str() on a (constructible) empty mitigations map.
        width = max((len(k) for k in self.mitigations), default=0)
        for cls in sorted(self.mitigations):
            lines.append("    %-*s : %s" % (width, cls, self.mitigations[cls]))
        rl = self.recommended_limits
        if rl is None:
            lines.append("  recommended opt-in limits: None")
        else:
            lines.append(
                "  recommended opt-in limits: max_depth=%s max_attributes=%s "
                "max_bytes=%s" % (rl.max_depth, rl.max_attributes, rl.max_bytes))
        if self.notes:
            lines.append("  notes:")
            for n in self.notes:
                lines.append("    - %s" % n)
        return "\n".join(lines)


def security_report():
    """Return a `SecurityReport` describing this runtime's XML-security posture.

    Read-only and deterministic: it reads only ``pyexpat`` constants and
    purexml's own floors — no parse, no I/O, no side effects, safe to call
    repeatedly or at import. It does **not** change parse behavior or hard-fail;
    it *informs* (the enforce-vs-warn policy stays a 1.0 decision).

    The ``mitigations`` map records, per attack class, where it is handled **on
    this runtime** — purexml's handlers (`BLOCKED`), the libexpat layer at this
    version (`EXPAT_MITIGATED`), an opt-in cap (`OPT_IN`), or nowhere (`LIVE`).
    """
    meets_safe = EXPAT_VERSION >= SAFE_EXPAT_VERSION
    meets_recommended = EXPAT_VERSION >= RECOMMENDED_EXPAT_VERSION

    mitigations = {
        # Always blocked by purexml's own default-on handlers, version-independent.
        "billion_laughs": BLOCKED,
        "quadratic_blowup": BLOCKED,
        "external_entity_xxe": BLOCKED,
        "external_dtd_retrieval": BLOCKED,
        # libexpat reparse-deferral (CVE-2023-52425), fixed in expat 2.6.0.
        "large_tokens_cve_2023_52425":
            EXPAT_MITIGATED if meets_safe else LIVE,
        # disproportionate dynamic memory — covered only at the recommended floor.
        "disproportionate_memory":
            EXPAT_MITIGATED if meets_recommended else LIVE,
        # structural DoS (depth / attributes / size) — purexml opt-in caps only.
        "structural_dos_depth_attrs_size": OPT_IN,
    }

    notes = []
    if not meets_recommended:
        cur = ".".join(map(str, EXPAT_VERSION))
        rec = ".".join(map(str, RECOMMENDED_EXPAT_VERSION))
        live = sorted(k for k, v in mitigations.items() if v == LIVE)
        notes.append(
            "libexpat %s is below the recommended floor %s: the expat-layer "
            "class(es) %s may be live on this runtime — upgrade Python or the "
            "system expat." % (cur, rec, ", ".join(live)))
    notes.append(
        "structural DoS (deep nesting / attribute floods / giant documents) is "
        "opt-in: pass RECOMMENDED_LIMITS (or your own Limits) to the parse entry "
        "point's limits= parameter to bound it.")
    notes.append(
        "external_dtd_retrieval=blocked means no fetch/resolution is attempted "
        "(default-on) — NOT that external-DTD/entity *declarations* are rejected: "
        "an unresolved SYSTEM/PUBLIC declaration still parses (no I/O), matching "
        "defusedxml. Pass forbid_dtd=True to reject the DOCTYPE outright.")

    # __new__ normalizes mitigations → read-only view and notes → tuple, so a plain
    # dict/list is fine here (see SecurityReport.__new__).
    return SecurityReport(
        expat_version=EXPAT_VERSION,
        expat_meets_safe_floor=meets_safe,
        expat_meets_recommended=meets_recommended,
        recommended_limits=RECOMMENDED_LIMITS,
        mitigations=mitigations,
        notes=notes,
    )
