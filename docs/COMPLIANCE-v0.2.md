# COMPLIANCE — purexml v0.2.0

Audit of the v0.2.0 implementation against the approved spec
[`v0.2.0_RFC_Specification.md`](v0.2.0_RFC_Specification.md). Environment of record:
CPython 3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#4](https://github.com/russalo/purexml/pull/4), branch `v0.2.0`. Suite: **87 passed,
1 gated-skip.**

## §2 Capabilities

| Req | Implementation | Status |
|---|---|---|
| `parse(source, parser=None, forbid_dtd=…, forbid_entities=…, forbid_external=…)` → hardened `ElementTree` | `_parser.parse` (via stdlib `ET.parse` driving the hardened `XMLParser`) | ✅ |
| `fromstringlist(sequence, …)` | `_parser.fromstringlist` — stdlib-parity extra (defusedxml lacks it; documented) | ✅ |
| `XML` alias, `tostring` re-export | `ElementTree.py` (`XML = fromstring`; stdlib `tostring`) | ✅ |
| Public hardened `XMLParser` (+ `XMLParse`/`XMLTreeBuilder` aliases) | `_parser.XMLParser`, `feed`/`close` compatible with `ET.parse` | ✅ |
| `forbid_*` knobs, defusedxml-identical defaults + signature | parameterized handler install; positional-or-keyword | ✅ |
| `DTDForbidden` (reachable only with `forbid_dtd=True`) | `errors.DTDForbidden` + `StartDoctypeDeclHandler` | ✅ |

## §3 Module layout / scope honesty

| Req | Evidence | Status |
|---|---|---|
| `purexml.ElementTree` canonical namespace (s/defusedxml/purexml/) | `src/purexml/ElementTree.py`; `test_literal_sed_migration`, `test_namespace_mirrors_defusedxml_shape` | ✅ |
| Unimplemented names absent → `AttributeError` (not silent wrong-parse) | `test_iterparse_absent_until_v03` | ✅ |
| Re-export `ParseError`+`tostring`; NOT `Element` (faithful to defusedxml) | `test_element_not_reexported_faithful_to_defusedxml` | ✅ |
| Top-level convenience re-exports retained | `__init__.py` | ✅ |

## §4–§5 Equivalence contract + acceptance bar

| Req | Evidence | Status |
|---|---|---|
| C14N same-parse equivalence per entry point | `test_v02_surface` (parse, str+bytes) + sweep: **parse 0 disagreements / 152 real docs** | ✅ |
| `forbid_*` knob-matrix equivalence (all 8, incl. unsafe combos) | `test_forbid_knob_matrix_equivalence` + sweep: **0 disagreements / 1,216 real combos** | ✅ |
| Attack battery per entry point; no-fetch/no-read proven | parse/fromstringlist block attacks; XXE via parse blocked with no network touched (leg-1 probe) | ✅ |
| `DTDForbidden` fires iff `forbid_dtd=True` | `test_forbid_dtd_raises_dtdforbidden`, `test_xmlparser_honors_forbid_dtd` | ✅ |
| No regression in `fromstring` | sweep unchanged: **340 / 0** | ✅ |
| Zero runtime deps; determinism; never-crash | unchanged guards; degenerate inputs match defusedxml/stdlib | ✅ |

## §6–§8 measure-first / scope / DoD

| Req | Status |
|---|---|
| §6 measure-first — confirmed defusedxml.ElementTree surface (notable: **no `fromstringlist`** → shipped as documented stdlib-parity extra) | ✅ |
| §7 out of scope — `iterparse` deferred to v0.3 (absent); minidom/sax/etc. deferred | ✅ |
| §8 four-leg review run | ✅ (see below) |

## Four-leg review — ALL FOUR RUN

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ clean (parse no-fetch, robustness, DTDForbidden edges, XMLParser single-use, bytes-file) |
| 2 — Gemini cross-model (read-only inline) | ✅ "No substantiated findings" |
| 3 — empirical sweep | ✅ fromstring 340/0, parse 152/0, knob matrix 1,216/0 |
| 4 — PR bots (Gemini Code Assist + Codex) | ✅ **2 findings, both grounded + fixed** (commit `74c19f3`) |

### Findings dispositions (PR#4)
- **Reference-cycle regression on error paths (both bots, real).** The v0.2 feed/close
  split skipped the v0.1.2 cycle-break on malformed/blocked input, retaining the heavy
  expat parser + partial tree until cyclic GC. Fixed: `_cleanup()` runs on every
  termination path. (The lightweight `XMLParser` shell still lingers in the exception
  traceback frame — universal Python behavior — so the regression test asserts the heavy
  refs are released.)
- **Unconditional `comment`/`pi` handlers (both bots, real).** `XMLParser(target=<core-only>)`
  raised `AttributeError` at init. Fixed: guard optional callbacks with `hasattr`, like the
  stdlib. Regression test added.

## Open items (non-blocking, tracked)
- `iterparse` → v0.3 (the hard, streaming piece).
- Adoption model / packaging / license → deferred to 1.0 (per ROADMAP).

## Verdict
**Compliant.** All capability, namespace, equivalence (per-entry-point + the full knob
matrix on real data), and four-leg-review requirements are met with grounded evidence; both
substantiated PR-bot findings are fixed with regression tests; CI green across 3.10–3.13.
Ready to merge.
