# COMPLIANCE — purexml v0.1.0

Audit of the v0.1.0 implementation against the approved spec
[`v0.1.0_RFC_Specification.md`](v0.1.0_RFC_Specification.md). Environment of record:
CPython 3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#1](https://github.com/russalo/purexml/pull/1), branch `v0.1.0`. Suite: **42 passed.**

## Capabilities

| Req | Requirement | Implementation | Status |
|---|---|---|---|
| **C1** | `fromstring(text) -> Element`, standard `xml.etree` Element, stdlib-only | `_parser.py` `fromstring` → `_HardenedParser` on `xml.parsers.expat` + `TreeBuilder` | ✅ |
| **C2** | blocked + malformed input raise clear, catchable errors; no expansion/fetch/read/hang/crash | blocks → `PureXMLError(ValueError)`; malformed → stdlib `ParseError`; `errors.py`, `_parser.py:feed_close` | ✅ |

## §3 equivalence contract

| Req | Evidence | Status |
|---|---|---|
| §3.1 pin to defusedxml defaults (`forbid_dtd=False, forbid_entities=True, forbid_external=True`) | confirmed by source read (`scratch/measure/`); handlers installed accordingly | ✅ |
| §3.2 block/allow matrix matched (block entity decls + external resolution; allow entity-free DTD + unresolved external-DTD decl) | adversarial battery + corpus sweep: every row matches oracle | ✅ |
| §3.2 blocking proactive at handler level, not via libexpat cap | bombs raise at the declaration; a sub-cap bomb expands on bare stdlib but is blocked here | ✅ |
| §3.3 own hierarchy, blocks subclass `ValueError`; malformed → stdlib `ParseError`; consumer migrates by import swap | `errors.py`; `test_misc.py`; scanner confirmed import-swap | ✅ |

## §4 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| §4.1 same-parse equivalence via `ET.canonicalize`, 0 disagreements | `test_equivalence.py` (str+bytes) + sweep: **340 real inputs, 0 disagreements** (332 parse-equal, 8 both-raise) | ✅ |
| §4.2 falsify-first attack battery incl. allow counter-cases | `test_attacks.py` + inline battery (quadratic, recursive, param, XXE file/net, external DTD, NOTATION, unparsed, char-ref, deep-nest, huge-attrs) | ✅ |
| §4.3 no-fetch/no-read proven via trip-wire + sentinel | `conftest.py::assert_no_io` (self-tested) + `test_sentinel_never_leaks` | ✅ |
| §4.4 zero runtime dependencies; no defusedxml import under `src/` | `test_misc.py::test_no_runtime_dependency_on_defusedxml`; grep clean | ✅ |
| §4.5 deterministic, never-crash-host, libexpat-version-independent | `test_determinism_repeated_parses_identical`; robustness battery (0 mismatches) | ✅ |

## §5 measure-first / §6 scope / §7 floor

| Req | Status |
|---|---|
| §5 enumerated defusedxml mitigation list + default config recorded | ✅ `scratch/measure/v0.1.0_measure_first_findings.md` |
| §5 corpus augmented past OOXML with allow/block boundary fixtures | ✅ `conftest.py` + 340-input real sweep |
| §6 no configurable `forbid_*` knobs; no parse modes beyond `fromstring`; no writing | ✅ |
| §7 runtime floor | `>=3.12` retained for v0.1.0 (lowerable later; no stdlib blocker) — tracked |

## §8 four-leg review — ALL FOUR RUN

| Leg | Result |
|---|---|
| 1 — in-house swarm (4 angles) | ✅ clean; 2 LOW dead-code notes kept by design (`scratch/review/v0.1.0_swarm_findings.md`) |
| 2 — Gemini cross-model (read-only inline) | ✅ "No substantiated findings" (flash; pro timed out — substitution recorded) |
| 3 — empirical sweep (340 real inputs) | ✅ 0 disagreements |
| 4 — PR bots (on PR #1) | ✅ Gemini Code Assist: 1 finding (reference cycle) — **grounded + fixed** (commit `456e806`, mirrors stdlib `XMLParser.close`, regression test added). Codex: "no major issues." |

### Findings dispositions
- **PR#1 / Gemini — expat-parser reference cycle (real, fixed).** `_HardenedParser`
  was reclaimable only by cyclic GC. Confirmed (weakref survived `del` under
  `gc.disable()`). Fixed in `feed_close` `finally` (clear `self.parser`/`self.target`);
  `test_no_reference_cycle_after_parse` guards it.
- **Leg 1 LOW dead-code ×2** (the `_default` `&`-branch; the `ExternalReferenceForbidden`
  backstop) — kept, faithful mirrors of stdlib/defusedxml. Not defects.

## Open items (non-blocking, tracked)
- Vendor single-file form (scanner #6) — deferred, Russell's call.
- Runtime floor — `>=3.12`, revisitable.

## Verdict
**Compliant.** All capability, equivalence, acceptance-bar, scope, and four-leg-review
requirements are met with grounded evidence; the single substantiated review finding is
fixed with a regression test; CI green. Ready to merge.
