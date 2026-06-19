# Security Policy

purexml **is a security control** — its job is to safely parse untrusted XML.
That raises the bar on this policy: a defect here is a security defect.

## Scope

purexml mirrors the `defusedxml.ElementTree` surface (`fromstring`, `parse`,
`iterparse`, `fromstringlist`, `XMLParser`, the `forbid_*` knobs) and, as of v0.10,
`defusedxml.minidom` (`parse`/`parseString`) — behaviorally equivalent to `defusedxml`
at its defaults. On **fully untrusted** XML input (the caller is trusted; the XML is the
attacker-controlled surface) it — across every entry point, including incremental
`iterparse` streaming and the minidom DOM builder:

- **blocks** entity-expansion bombs (billion-laughs / quadratic), XXE via
  external entities (local file + network), and external reference resolution —
  raising a catchable exception **at the entity declaration, before any
  expansion or resolution** (independent of the system libexpat version);
- **never** fetches external resources, reads local files referenced by the XML,
  expands an entity bomb, hangs, consumes unbounded CPU/memory, or crashes the
  host process. Blocked/malformed input always yields a catchable exception.

Beyond the mirror, `security_report()` (v0.5) is **read-only introspection** — it
reports this runtime's posture (libexpat version + per-class mitigation layer +
the opt-in `Limits` preset) and **does not change parse behavior or hard-fail**;
the enforce-vs-warn policy is a 1.0 decision. The structural-DoS caps (`Limits`,
v0.4) are **opt-in, default-off**, so they never alter the strict-mirror default.

It is stdlib-only (`xml.parsers.expat` + `xml.etree`) with **zero runtime
dependencies**, so the host process inherits no third-party parser attack surface.
As of v0.3.1 this is enforced **structurally**: a CI-gated test (`tests/test_no_io.py`)
asserts `src/` imports only the stdlib `xml` package — no `socket`/`urllib`/`http`/
`subprocess`/`os`/… — so purexml cannot reach the network or filesystem at all (the
behavioral no-fetch proof, now backed by a structural one).

## Reporting vulnerabilities

The repo is private (russalo tailnet). Report privately to the maintainer —
**russalo@gmail.com**. **Do not** open a public issue. Russalo default
acknowledgement: 48 hours / initial assessment 7 days.

When reporting, include the **exact input** that triggers the issue (a parse that
should have been blocked but wasn't, an unexpected fetch/read, a crash/hang, or a
divergence from `defusedxml`) — purexml's whole contract is grounded in
constructable failing inputs.

## Supported versions

Pre-1.0: the current minor is supported; older is not (please upgrade). At 1.0 this
becomes a binding policy (the latest minor; security fixes backported per the
then-published support window).

| Version | Supported |
|---|---|
| 0.10.x | Yes (current) |
| < 0.10 | No (pre-1.0 moves fast; upgrade) |

## Security advisories & CVE handling

How a confirmed vulnerability is handled, once triaged against the real code (every
report is reproduced from its failing input before it counts):

1. **Reproduce + assess** — construct the failing input, confirm it's real, rate severity.
2. **Fix on a private branch** with a regression test that fails before / passes after,
   under the four-leg review (the adversarial leg carries extra weight here).
3. **Release** a patch on the supported minor (and backport per the support window).
4. **Disclose** — publish a security advisory with the affected versions, the fixed
   version, and a workaround if any; credit the reporter unless they decline.
5. **Coordinated disclosure** — we ask reporters to hold public disclosure until a fix
   ships or a reasonable window elapses; we aim to move quickly on a security control.

A distinct class is **libexpat-layer** issues: some XML-DoS protection lives in libexpat,
not purexml. For those, the fix is *upgrade your runtime's expat* — and
`purexml.security_report()` / `python -m purexml` already tell you whether yours is
current (see *Maintenance policy*). purexml advisories cover the purexml layer; we surface
the libexpat dimension rather than claim to fix it.

> [[STRATEGIC: at publish, the private channel below is joined by a public one —
> GitHub Security Advisories / a `SECURITY` contact — and a concrete disclosure window.]]

## Maintenance policy

purexml's reason to exist beyond a one-time mirror is that it is **maintained where the
incumbent froze.** Concretely, that means:

- **Tracks libexpat.** A standing gate (`tools/check_expat_currency.py`) checks the latest
  libexpat against the recommended floor before every release and when the security code
  changes; new reachable attack classes are added to `security_report()`, gated on their
  fix version. (Done twice already: the 2026 expat 2.7.4–2.8.1 DoS train was folded in
  within days.)
- **Proven per release.** Every release is differentially tested against the `defusedxml`
  oracle (C14N-equivalent-or-both-raise) over a real corpus + a fuzzer; the result is a
  committed [`docs/EQUIVALENCE.md`](docs/EQUIVALENCE.md). New XML-attack research becomes
  new corpus + tests.
- **Independent adversarial soak per cycle.** A standing external attack battery
  (out-of-tree, run by a separate reviewer) soaks each release — XML bombs, XXE, external
  entities/DTD, XInclude — judging on raw evidence (timed-out / mem-exceeded / escaped).
  Green at every release to date; any non-survival is a real finding.
- **Reviewed.** Every change runs the four-leg decorrelated review; findings are grounded
  against the real code before action.

These are practices we run today, stated so adopters can rely on them — not an SLA promise.

## Dependency security

| Dependency | Role | Posture |
|---|---|---|
| *(none)* | runtime | **Zero runtime dependencies** — stdlib only. No third-party parser/native code in the import path; nothing to compromise via the dependency surface. |
| `defusedxml` | dev/test **oracle** | Never shipped, never imported under `src/` (guarded by a test). Used only to validate equivalence. |
| `pytest` | dev/test | test runner only |
| `atheris` | dev/test (`[fuzz]` extra) | Opt-in coverage-guided fuzzing only (`fuzz/`). Never shipped, never imported under `src/`. |

## The bounds any change must preserve

purexml's security guarantees are a **checklist for every change**, not a
one-time setup. Any new code path (especially a new parse mode) MUST inherit:

- **proactive blocking** of entity declarations and external resolution (never
  rely on libexpat's amplification cap — a sub-cap bomb expands without it);
- **no I/O on untrusted input** — no socket, no file open, no external fetch
  (the test battery proves this with a socket/open/urlopen trip-wire);
- **catchable failure** — a `PureXMLError` (a `ValueError`) or stdlib
  `ParseError`, never an uncatchable error or host crash;
- **behavioral equivalence to the `defusedxml` oracle** — verified by the C14N
  same-parse sweep; do not over-block (it breaks equivalence) or under-block.

A new IO/parse surface is exactly where this bug class re-emerges; the
falsify-first battery + corpus sweep are the gate.
