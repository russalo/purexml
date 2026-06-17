# COMPLIANCE — purexml v0.4.0

Audit of v0.4.0 against the approved spec
[`v0.4.0_RFC_Specification.md`](v0.4.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#7](https://github.com/russalo/purexml/pull/7), branch `v0.4.0`. Suite: **127 passed,
1 gated-skip.**

## §2 Identity (ratified)
purexml is now **"strict defusedxml mirror by default, plus opt-in defense-in-depth."**
The default path (`limits=None`) stays byte-equivalent to defusedxml; the caps are
additive opt-in. ✅ ratified 2026-06-16; recorded in CLAUDE.md Known decisions.

## §3–§4 Capability + design

| Req | Implementation | Status |
|---|---|---|
| `Limits(max_depth, max_attributes, max_bytes)`, default `None` = no cap | `limits.py` (namedtuple) | ✅ |
| `LimitExceeded` ← `DepthExceeded`/`AttributesExceeded`/`SizeExceeded` (all `PureXMLError`/`ValueError`) | `errors.py` | ✅ |
| `RECOMMENDED_LIMITS` preset, measured | `limits.py` (1000 / 256 / 100 MiB) | ✅ |
| keyword-only `limits=` on `fromstring`/`parse`/`fromstringlist`/`iterparse`/`XMLParser` | `_parser.py` (defusedxml positional compat preserved) | ✅ |
| Enforced in `_start`/`_end` (depth/attrs) + `feed` (bytes) — incl. mid-stream | `_parser.py` | ✅ |

## §5 Acceptance bar

| Req | Evidence | Status |
|---|---|---|
| Default-off == strict mirror (byte-identical) | full equivalence suite + sweep **372/0**; `test_default_off_equals_oracle` (`limits=None` ≡ omitted) | ✅ |
| Caps fire at threshold; one below parses | `test_max_depth`/`test_max_attributes`/`test_max_bytes` | ✅ |
| Enforced under streaming (iterparse) | `test_limits_under_iterparse_streaming` | ✅ |
| `RECOMMENDED_LIMITS` no false positives; catches pathology | `test_recommended_limits_*` (measured vs 584 real parts: depth 24 / attrs 18 / 580 KB) | ✅ |
| Deterministic; catchable; never-crash (cap raises before the RecursionError/OOM) | exception hierarchy; cleanup-on-error | ✅ |

## §6 Measure-first
Profiled 584 real OOXML/tika parts → max depth 24, max attrs 18, max ~580 KB. Set
`RECOMMENDED_LIMITS` (1000 / 256 / 100 MiB) with generous headroom — 0 false positives.

## Four-leg review — ALL FOUR RUN

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ clean (depth tracks nesting not count; security-blocking precedence; cleanup-on-error; unset caps inert) |
| 2 — Gemini cross-model (read-only inline) | ✅ "No substantiated findings" |
| 3 — empirical sweep (default-off) | ✅ 372/0 — strict mirror intact |
| 4 — PR bots | ✅ **4 findings, all real, all fixed** (commit 657cb6d) |

### Findings dispositions (PR#7) — all grounded + fixed
- **Codex — depth/attr accounting tied to target callbacks (P2, real bug).** A custom
  target with `start` but no `end` never decremented depth → spurious `DepthExceeded`
  on wide-but-shallow docs. Fixed: install `_start`/`_end` whenever a cap needs them,
  independent of the target; regression test added. (My default-target tests missed it.)
- **Codex — `max_bytes` counted code points, not bytes, for str (P2, real).** A 407-byte
  emoji doc passed a 350-byte cap. Fixed: count UTF-8 bytes for str (already
  materialized → no new DoS surface); regression test added.
- **Gemini ×2 — `parse`/`fromstringlist` leaked the parser cycle (high)** if the source
  read / sequence iteration raised before feed/close. Fixed: `try/finally` cleanup for
  the internally-created parser (caller-supplied parsers untouched); regression tests.

## Open items / freeze note
- At 1.0 freeze this surface is **PROVISIONAL** (per ROADMAP) — the cap names, the
  `Limits` shape, and `RECOMMENDED_LIMITS` values may evolve; opt-in, default-off stays.

## Verdict
**Compliant.** Opt-in structural-DoS caps shipped, default-off strict mirror proven
intact (372/0), four-leg review run with all four PR-bot findings grounded and fixed.
CI green 3.10–3.13. Ready to merge.
