# Security Policy

purexml **is a security control** — its job is to safely parse untrusted XML.
That raises the bar on this policy: a defect here is a security defect.

## Scope

purexml mirrors the `defusedxml.ElementTree` surface (`fromstring`, `parse`,
`iterparse`, `fromstringlist`, `XMLParser`, the `forbid_*` knobs), behaviorally
equivalent to `defusedxml` at its defaults. On **fully untrusted** XML input (the
caller is trusted; the XML is the attacker-controlled surface) it — across every
entry point, including incremental `iterparse` streaming:

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

Pre-1.0: the current minor is supported; older is not (please upgrade).

| Version | Supported |
|---|---|
| 0.5.x | Yes (current) |
| < 0.5 | No (pre-1.0 moves fast; upgrade) |

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
