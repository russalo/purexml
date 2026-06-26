# COMPLIANCE — purexml v0.11.0

Audit of v0.11.0 against the approved spec
[`v0.11.0_RFC_Specification.md`](v0.11.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#30](https://github.com/russalo/purexml/pull/30), branch `v0.11.0-expat-2.8.2-map`.
Suite: **218 passed, 1 gated-skip.**

## Theme
Map the reachable libexpat 2.8.2 integer-overflow batch into `security_report().mitigations` —
the follow-up to v0.10.1's floor patch (the v0.5.1→v0.6 lifecycle). **Report-only — no
parse-behavior change.**

## §2 scope + §3 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| Aggregate class `integer_overflow_dos_expat_2_8_2` (design Q1/Q2) | `_expat_security.py` mitigations map | ✅ |
| `EXPAT_MITIGATED` ≥2.8.2 else `LIVE`, gated on `_INTEGER_OVERFLOW_BATCH_FIXED=(2,8,2)` | per-class constant, decoupled from the moving floor | ✅ |
| 7 reachable CVEs covered, listed in a dedicated live-note | storeAtts 56403 / addBinding 56404 / getAttributeId 56405 / XML_ParseBuffer 56406 / textLen 56407 / copyString 56408 / doProlog 56132 | ✅ |
| Retire the v0.10.1 interim `_HIGHEST_UNMAPPED_FIX` + generic gap clause (Q3) | removed; below-floor advisory names the LIVE class | ✅ |
| Unreachable classes NOT mapped (grounded) | 50219/56131/56412 (reentrant/suspend-resume), 56409–56411 (xmlwf) — recorded | ✅ |

## §5 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| No parse-behavior change; no new runtime dep; no-I/O guard holds; mirror byte-equivalent | diff confined to `_expat_security.py` + tests + docs; empirical sweep **372/0** | ✅ |
| Class version-gated correctly (LIVE <2.8.2, MITIGATED at/above) | `test_version_gating` `intov` column across (2,5,0)…(2,9,0) | ✅ |
| Generic untracked-gap clause gone; LIVE class named below floor | `test_floor_advisory_names_mapped_batch_no_generic_gap` (no "untracked"/"not yet individually tracked"; class named; 7-CVE note) | ✅ |
| Read-only / deterministic / immutable; `as_dict()`/`--json` pass the new key | unchanged construction path; inline JSON round-trip probe | ✅ |
| Docs freshness sweep; HISTORY row; four-leg; this compliance | done (HISTORY, CLAUDE, ROADMAP, SECURITY supported-versions) | ✅ |

## §6 grounding
Each 2.8.2 CVE's reachability grounded before mapping
(`scratch/review/v0.11.0_grounding_expat_2_8_2.md`): 7 reach ordinary attribute/namespace/text/
DOCTYPE parsing → mapped (one aggregate, shared 2.8.2 fix version). The reentrant-handler /
suspend-resume trio (50219/56131/56412) requires reentrant parser calls from handlers or
suspend/resume — purexml does one-shot parsing only → **not reached**; the xmlwf trio
(56409–56411) is the CLI utility → **not reached**. Recorded, not mapped.

## Four-leg review — ALL FOUR RUN (report-only tier)

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ no findings. Gating correct across versions; never under-reports (LIVE named); decoupled from other classes; no stale gap wording; JSON round-trips. |
| 2 — Gemini cross-model (`gem.sh`) | ⚠️ UNAVAILABLE (daily free-tier quota exhausted, 429, 2026-06-26). Covered by the leg-1 decorrelated inline probe + leg-4 bots. |
| 3 — empirical sweep | ✅ ElementTree mirror **372/0** — mirror untouched. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ Gemini: clean. Codex: 1 P2 (SECURITY supported-versions stale) — real, **fixed**. |

### Findings dispositions
- **Codex P2 — SECURITY.md supported-versions stale.** The release bumps to 0.11.0 but the
  *Supported versions* table still read 0.10.x / <0.10. Real doc-freshness miss (the table is where
  reporters learn which line gets fixes). **Fixed:** 0.11.x current / <0.11 unsupported.
- Gemini Code Assist: no review comments.

## Freeze note
The `mitigations` map is **PROVISIONAL** at 1.0 (per ROADMAP) — keys/fix-versions evolve as
libexpat moves; the defusedxml-mirror surface is the frozen part. The report informs, never enforces.

## Verdict
**Compliant.** The 2.8.2 reachable batch mapped per the approved RFC (grounded; one aggregate
class); the interim gap marker retired; no parse-behavior change, mirror proven byte-equivalent
(372/0); four-leg run with the one PR-bot finding grounded + fixed. CI green 3.10–3.13. Ready to merge.
