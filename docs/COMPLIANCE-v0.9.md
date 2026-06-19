# COMPLIANCE — purexml v0.9.0

Audit of v0.9.0 against the approved spec
[`v0.9.0_RFC_Specification.md`](v0.9.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#27](https://github.com/russalo/purexml/pull/27), branch `v0.9.0-hash-flooding-map`.
Suite: **184 passed, 1 gated-skip.**

## Theme
Map **CVE-2026-41080** (hash-flooding via insufficient SipHash salt entropy) into the
`security_report()` posture map — the class v0.6 deferred "until grounded". Grounded as
reachable; mapped with a new non-overstating status. **Report-only — no parse-behavior change.**

## §2 scope + §3 status model (resolved to the approved leans, refined in review)

| Req | Implementation | Status |
|---|---|---|
| New class `hash_flooding_cve_2026_41080` (CVE-tagged key, design Q2) | `_expat_security.py` mitigations map | ✅ |
| New 5th status `EXPAT_PARTIAL` (design Q1/B-i) — exported, documented, distinct | `__all__` (`__init__` + `_expat_security`); `SecurityReport` docstring status list | ✅ |
| **Never `LIVE`** (hardening-not-hole; bare `LIVE` would overstate) | `test_version_gating` never-`LIVE` assertion across full sweep | ✅ |
| Never a version-only `MITIGATED` (CVE-2026-7210 two-layer — PR-bot refinement) | reported `EXPAT_PARTIAL` on every runtime; note carries the pyexpat requirement | ✅ |
| Retire `_HIGHEST_UNMAPPED_FIX` + generic untracked-gap advisory | removed; below-floor note names only tracked `LIVE` classes | ✅ |
| `_HASH_FLOODING_FIXED = (2,8,0)` retained to drive the note | per-class constant | ✅ |
| Version v0.9.0; full report-only-minor flow (Q3) | `pyproject.toml` + `__version__` = 0.9.0; RFC + this compliance | ✅ |

## §5 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| No parse-behavior change; no new runtime dep; no-I/O guard holds | diff confined to `_expat_security.py` + `__init__` exports + tests + docs; `_parser.py`/handlers/defaults untouched | ✅ |
| Default mirror byte-equivalent | empirical sweep **372/0**; full suite incl. differential fuzz green | ✅ |
| Class version-gated correctly; **never `LIVE`** | `test_version_gating` (rows 2.5.0 → 2.9.0; hashf = PARTIAL every row) + explicit never-`LIVE` assert | ✅ |
| Two-layer honesty — never false-green on expat alone | `test_hash_flooding_always_partial_two_layer` (PARTIAL at 2.7.4 AND 2.8.1; note cites CVE-2026-7210 at/above 2.8.0) | ✅ |
| Floor advisory no longer claims an untracked gap | `test_floor_advisory_no_longer_claims_untracked_gap` (no "untracked"/"not individually tracked" wording; live class still named) | ✅ |
| Read-only / deterministic / immutable report intact | unchanged construction path (`MappingProxyType` + tuple); `as_dict()`/`--json` pass key+status through | ✅ |

## §6 measure-first / grounding
CVE-2026-41080 grounded (`scratch/review/v0.9.0_grounding_cve_2026_41080.md`): insufficient
SipHash salt entropy (CWE-331, expat 2.8.0, LOW), reachable via normal name-interning →
mapped. The two NULL-deref classes (CVE-2026-24515 @ 2.7.4, CVE-2026-32776 @ 2.7.5) stay
unmapped (purexml does not reach them). With 41080 mapped, every *reachable* expat fix is
individually tracked → the generic untracked-gap advisory was retired.

## Four-leg review — ALL FOUR RUN (scaled to the report-only surface)

| Leg | Result |
|---|---|
| 1 — in-house (1 decorrelated finder, inline grounded probes) | ✅ no findings — `--check` version-only (PARTIAL doesn't leak); full version sweep → never `LIVE`, no under-reporting; JSON round-trips. |
| 2 — Gemini cross-model (`gem.sh`) | ✅ "No defects found. The changes are ready for v0.9.0." |
| 3 — empirical sweep | ✅ **372/0** — mirror byte-identical. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ Gemini: clean. Codex: **1 P2 — real, grounded, fixed** (CVE-2026-7210 two-layer; commit `b89c01e`). |

### Findings dispositions — grounded; nothing declined
- **Codex P2 (leg 4):** "Require the pyexpat salt fix before MITIGATED." Even at expat ≥2.8.0,
  CPython's `pyexpat` kept calling the 4–8-byte `XML_SetHashSalt` until patched to
  `XML_SetHashSalt16Bytes` ([CVE-2026-7210](https://nvd.nist.gov/vuln/detail/CVE-2026-7210),
  [gh-149018](https://github.com/python/cpython/issues/149018)) — so gating `MITIGATED` on the
  expat version alone is a false-green. **Web-grounded before fixing** (NVD + CPython issue;
  pyexpat sets the salt itself — confirmed). **Fixed:** `hash_flooding` reports `EXPAT_PARTIAL`
  on every runtime (never version-only `MITIGATED`); note surfaces the pyexpat requirement; RFC
  §3 records the refinement; tests updated. Re-ran gates green.
- Gemini Code Assist: no review comments (only the consumer-tier sunset notice — not a finding).

## Freeze note
The `SecurityReport.mitigations` map **and the status vocabulary** (incl. the new
`EXPAT_PARTIAL`) are **PROVISIONAL at 1.0** (per ROADMAP) — they may evolve as libexpat/pyexpat
move; the defusedxml-mirror surface is the frozen part. The report *informs*, never enforces.

## Verdict
**Compliant.** CVE-2026-41080 mapped per the approved RFC (with the grounded two-layer
refinement); no parse-behavior change, mirror proven byte-equivalent (372/0); four-leg review
run with the one PR-bot finding grounded and fixed. CI green 3.10–3.13. Ready to merge.
