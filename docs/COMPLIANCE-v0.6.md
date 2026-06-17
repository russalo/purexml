# COMPLIANCE — purexml v0.6.0

Audit of v0.6.0 against the approved spec
[`v0.6.0_RFC_Specification.md`](v0.6.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#11](https://github.com/russalo/purexml/pull/11), branch `v0.6.0`. Suite: **168 passed,
1 gated-skip.**

## Theme
Complete the `security_report()` posture map: the two 2026 expat-layer DoS classes that
reach purexml's normal parse paths (surfaced by v0.5.1's floor review) become first-class
`mitigations` entries. **Report-only — no parse-behavior change.**

## §2 Capability + §4 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| `content_token_overflow_cve_2026_25210` → `EXPAT_MITIGATED` iff expat ≥ 2.7.4 else `LIVE` | `_expat_security.py` (`_CONTENT_TOKEN_OVERFLOW_FIXED`) | ✅ |
| `attribute_collision_dos_cve_2026_45186` → `EXPAT_MITIGATED` iff expat ≥ 2.8.1 else `LIVE` | `_expat_security.py` (`_ATTRIBUTE_COLLISION_FIXED`) | ✅ |
| CVE-tagged keys (design Q1) | match `large_tokens_cve_2023_52425` | ✅ |
| `attribute_collision` ↔ `max_attributes` = option (a): gate on expat, note the lever (Q2) | conditional note when class is `LIVE` | ✅ |
| Trim generic advisory, still surface the unmapped gap (Q3) | `_HIGHEST_UNMAPPED_FIX` gates the 41080 clause | ✅ |
| Each class gates on its OWN fix version, not the moving floor | per-class constants | ✅ |
| CVE-2026-41080 left unmapped (ungrounded), covered by advisory | documented gap | ✅ |

## §5 Acceptance bar

| Req | Evidence | Status |
|---|---|---|
| No parse-behavior change; no new runtime dep; no-I/O guard holds | diff confined to `_expat_security.py` + tests + RFC; `_parser.py`/handlers/defaults untouched | ✅ |
| Default mirror byte-equivalent | empirical sweep **372/0**; full suite incl. fuzz green | ✅ |
| Both new classes version-gated correctly (below/at each fix) | `test_version_gating` (rows 2.5.0 → 2.9.0 incl. 2.7.4, **2.8.0**, 2.8.1 boundaries) | ✅ |
| Advisory accuracy — never overstate, never under-report | `test_recommended_gap_always_names_unmapped_cve` (41080 cited <2.8.0, NOT at 2.8.0; live class always named) | ✅ |
| `max_attributes` lever surfaced only when collision class is live | `test_attribute_collision_live_surfaces_max_attributes_lever` | ✅ |
| Read-only / deterministic / immutable report intact | unchanged construction path (`MappingProxyType` + tuple) | ✅ |

## §6 Measure-first
Per-CVE grounding (v0.5.1 + this slice): 25210 (`doContent` overflow, fixed 2.7.4) and
45186 (quadratic attr-name checks, fixed 2.8.1) reach normal parse paths → mapped. 24515
(needs an encoding handler purexml never sets) and 32776 (blocked external param entities)
do not reach purexml → not mapped. 41080 (2.8.0) ungrounded → left unmapped, covered by the
generic advisory only when the runtime is actually below 2.8.0.

## Four-leg review — ALL FOUR RUN (scaled to the report-only surface)

| Leg | Result |
|---|---|
| 1 — in-house (1 decorrelated finder) | ✅ correct-by-design; gates, scope, 7→8-row test table, advisory, lever note, immutability all verified. 1 LOW pre-existing doc-drift finding → fixed. |
| 2 — Gemini cross-model (`gem.sh`) | ✅ "correct-by-design… No defects found. Clear to merge." |
| 3 — empirical sweep | ✅ **372/0** — mirror byte-identical. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ Codex no suggestions; Gemini 1 finding (2.8.0 advisory precision) — real, **fixed** (commit 5f17a98). |

### Findings dispositions — grounded; nothing declined
- **Pre-open LOW (leg 1):** `SecurityReport` docstring said `RECOMMENDED (2.7.2)`; constant
  is 2.8.1 (drift from the v0.5.1 bump). Fixed in the freshness sweep.
- **PR-bot (leg 4) — Gemini medium/security:** at exactly expat 2.8.0 the advisory cited
  "may be missing CVE-2026-41080", but 41080 was fixed in 2.8.0 → overstated. Gated the
  untracked-gap clause on `EXPAT_VERSION < 2.8.0`; mapped LIVE classes still always named
  (no under-report). 2.8.0 boundary row + assertion added.
- Codex: no suggestions.

## Freeze note
The `SecurityReport.mitigations` map is **PROVISIONAL at 1.0** (per ROADMAP) — keys and the
per-class fix-versions may evolve as libexpat moves; the defusedxml-mirror surface is the
frozen part. The report *informs*, never enforces.

## Verdict
**Compliant.** The posture map completed per the approved RFC; no parse-behavior change,
mirror proven byte-equivalent (372/0); four-leg review run with the one PR-bot finding
grounded and fixed. CI green 3.10–3.13. Ready to merge.
