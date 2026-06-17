# purexml Version History

This is the running index of all versions, their specifications, and their
compliance reports. Use this as the **entry point** when orienting on the
project — it's the one document where every release leaves a row.

**Current version:** see the project's version source-of-truth (e.g.
`pyproject.toml`, the `VERSION` constant, or `go.mod`) and the latest entry
below.

**How to read this index:**
- Active versions have specs and compliance reports in `docs/`.
- Archived versions have specs and compliance reports under `docs/archive/`
  (convention: at the first major bump, the previous major's RFCs and
  compliance reports move into `docs/archive/{previous_major}.x/`).
- Pre-1.0 versions use **looser formatting** — narrative entries, no
  compliance report requirement, RFCs optional. Once the project ships 1.0
  the row shape below becomes mandatory; the public contract binds at the
  same time.

---

## Versions

| Version | Schema | Date | Notable | Spec | Compliance |
|---|---|---|---|---|---|
| 0.3.0 | n/a | 2026-06-16 | Hardened `iterparse` — **completes the `defusedxml.ElementTree` family** (the streaming slice). Reuses stdlib `iterparse` via `_setevents` on `purexml.XMLParser` (Option A). Merged via PR #5; four-leg review complete (all 3 PR-bot findings grounded-declined). SCHEMA n/a; LOGIC unchanged (default behavior; adds the streaming entry point). | [v0.3.0_RFC_Specification.md](docs/v0.3.0_RFC_Specification.md) | [COMPLIANCE-v0.3.md](docs/COMPLIANCE-v0.3.md) |
| 0.2.0 | n/a | 2026-06-16 | Complete the non-streaming `defusedxml.ElementTree` surface: `parse`, `fromstringlist`, `XML`/`tostring`, exposed `XMLParser`, the `forbid_*` knobs (+ new `DTDForbidden`), under a canonical `purexml.ElementTree` namespace. Merged via PR #4; four-leg review complete. SCHEMA n/a; LOGIC mitigation set extended (`forbid_dtd` path), default behavior unchanged. | [v0.2.0_RFC_Specification.md](docs/v0.2.0_RFC_Specification.md) | [COMPLIANCE-v0.2.md](docs/COMPLIANCE-v0.2.md) |
| 0.1.2 | n/a | 2026-06-16 | **Patch** — durability hardening: differential fuzz gate vs the defusedxml oracle (seeded, C14N-equal-or-both-raise), the 2 newer expat-layer attack classes (CVE-2023-52425 large-tokens + disproportionate-memory, version-gated), and an opt-in libexpat version-awareness API (`EXPAT_VERSION` / `expat_is_secure` / `assert_expat_secure`). No parse-behavior change; LOGIC unchanged (v0.1), SCHEMA n/a. _(HISTORY only, no RFC — part of v0.1.)_ | _(no RFC — patch)_ | _(part of v0.1)_ |
| 0.1.1 | n/a | 2026-06-16 | **Patch** — lower runtime floor to Python **3.10** (was 3.12) so purexml never binds a consumer's Python floor (target spec §4); add a CI matrix (3.10–3.13) to test the declared floor rather than only 3.12. No logic/behavior change; SCHEMA n/a, LOGIC unchanged (v0.1). _(HISTORY only, no RFC — part of v0.1.)_ | _(no RFC — patch)_ | _(part of v0.1; see [COMPLIANCE-v0.1.md](docs/COMPLIANCE-v0.1.md))_ |
| 0.1.0 | n/a | 2026-06-16 | First slice: hardened `fromstring` — C1 safe-parse + C2 safe-failure, behaviorally equivalent to `defusedxml` defaults, stdlib-only. SCHEMA n/a (returns stdlib `Element`); LOGIC introduced (hardening mitigation set v0.1). Merged via PR #1; four-leg review complete. | [v0.1.0_RFC_Specification.md](docs/v0.1.0_RFC_Specification.md) | [COMPLIANCE-v0.1.md](docs/COMPLIANCE-v0.1.md) |
| 1.0.0 | 1.0 | YYYY-MM-DD | **Schema freeze.** Public contract binding. Backward compatibility policy in effect. No new features — governance declaration on a validated codebase. | [v1.0.0_RFC_Specification.md](docs/v1.0.0_RFC_Specification.md) | [COMPLIANCE-v1.0.md](docs/COMPLIANCE-v1.0.md) |
| 1.0.1 | 1.0 | YYYY-MM-DD | **Patch release** — example shape. Bug fix in {component}. SCHEMA unchanged. _(part of v1.0; HISTORY only, no RFC.)_ | _(no RFC — patch)_ | _(part of v1.0)_ |

---

## Drafts in Flight

List any RFCs currently in draft (`docs/v{X.Y.Z}_RFC_DRAFT.md`). When none are
open, state so explicitly rather than deleting the section — the empty-but-named
state is the signal:

> No drafts in flight. The **`defusedxml.ElementTree` family is complete** as of
> v0.3.0; the build axis to 1.0 is done. Remaining work is adoption validation +
> the freeze ceremony — see [`docs/ROADMAP-to-1.0.md`](docs/ROADMAP-to-1.0.md). No
> RFC is open; the next RFC is the v1.0 freeze when adoption + the deferred
> decisions land.
>
> (Shipped 2026-06-16: v0.1.0 fromstring (PR #1); v0.1.1 floor→3.10 (PR #2); v0.1.2
> durability + expat awareness (PR #3); v0.2.0 non-streaming ElementTree surface +
> forbid_* knobs (PR #4); v0.3.0 iterparse — family complete (PR #5).)

---

## Historical Drafts and Design Documents

These are working documents from earlier in the project. Kept for design
history; not specifications themselves. Pre-RFC scratch material (early
design notes, alternate drafts) lives here once promoted out of `scratch/`.

| File | Era | Purpose |
|---|---|---|
| TODO | Pre-vX.Y | TODO: short description of what this is |

---

## Compliance Report Gaps

TODO: Note any versions that did **not** get a compliance report and why
(usually patch releases — they're covered by HISTORY narrative + the
parent minor's compliance report). Default rule:

> Patches inherit their parent minor's compliance report; their narrative
> lives in this index, not in a separate report.
