# COMPLIANCE — purexml v0.10.0

Audit of v0.10.0 against the approved spec
[`v0.10.0_RFC_Specification.md`](v0.10.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#28](https://github.com/russalo/purexml/pull/28), branch `v0.10.0-minidom`. Suite:
**217 passed, 1 gated-skip.**

## Theme
First breadth beyond ElementTree — `purexml.minidom` (a hardened drop-in for
`defusedxml.minidom`) + `purexml.common` (exception-compat shim). Scope grounded by measured
defusedxml usage (minidom = 457 sites, #2 surface). Implements the 2026-06-19 scope reframe.

## §2 scope + §3 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| `purexml.minidom.parse` / `parseString` → stdlib `Document`, defusedxml signature + defaults | `minidom.py` | ✅ |
| Hardening via subclass of stdlib `xml.dom.expatbuilder` (`_DefusedExpatBuilder`/`NS`), same blocking handlers as `_parser.py` | `minidom.py` `install()` | ✅ |
| Custom `parser=` → `NotSupportedError` (security-first; §3 opt-b) | `parse`/`parseString` guard | ✅ |
| `bufsize=` accepted for compat, no result change | documented; `Document` identical | ✅ |
| `purexml.common`: 4 names + `NotSupportedError` + `DefusedXmlException = PureXMLError` alias (compat layer only) | `common.py` | ✅ |
| `NotSupportedError(PureXMLError)` added | `errors.py` | ✅ |
| Eager-import `minidom` + `common` (parity with ElementTree) | `__init__` | ✅ |

## §5 acceptance bar

| Req | Evidence | Status |
|---|---|---|
| Match `defusedxml.minidom`: signature/defaults; allow-path Documents equivalent; attacks block with same exception types; malformed → stdlib error | oracle parity tests (9 ALLOW `toxml`-equal; 6 attacks block on both); `test_attacks_block_*` | ✅ |
| **No I/O on untrusted input** on the minidom path | `test_attacks_block_..._no_io`, `test_unparsed_ndata_entity_blocked`, `test_external_ref_backstop...`, `test_external_dtd_allowed_but_never_fetched` (F2 no-fetch) | ✅ |
| `purexml.common` provides the names; `except DefusedXmlException` catches a block; custom parser → `NotSupportedError` | `test_common_shim_is_drop_in_for_catch_sites`, `test_custom_parser_not_supported` | ✅ |
| no-I/O structural guard passes (only `xml` stdlib under `src/`); mypy `--strict` + ruff clean; coverage ≥90% | CI lint + `test_no_io`; minidom+common **100%** | ✅ |
| Docs freshness sweep; HISTORY row; full four-leg; this compliance | done (incl. ROADMAP scope promotion + Excluded `lxml`) | ✅ |

## Four-leg review — ALL FOUR RUN (feature minor, security-load-bearing → full depth)

| Leg | Result |
|---|---|
| 1 — in-house (inline grounded probes) | ✅ no findings. Verified DOM no-fetch on the F2 external-DTD edge; both backstops (NDATA / external-ref) fire; custom-parser refusal. minidom+common 100% cov. |
| 2 — Gemini cross-model (`gem.sh`, full pass) | ✅ **APPROVED — no defects** (no-fetch default+backstop, MRO/`install()` correct, refusal stricter than defusedxml). |
| 3 — empirical sweep | ✅ ElementTree mirror **372/0** (untouched) + in-suite oracle parity. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ Codex 1 P2 (builder-cycle on error) — real, grounded, **fixed** (`300ae30`). Gemini 1 medium (pathlib) — false premise, **declined** + parity pinned. |

### Findings dispositions — grounded; nothing waved through
- **Codex P2 — builder↔parser cycle on parse errors:** stdlib `ExpatBuilder` clears `_parser`
  only on success; malformed/blocked payloads leave a cycle for cyclic GC. Grounded via weakref
  (not refcount-reclaimable on error; defusedxml shares it). Fixed: `parseString`/`parseFile`
  `try/finally: self._parser = None` — builder now reclaimed on malformed AND blocked paths; no
  parse-result change. Regression test added. Matches the ElementTree refcount guarantee.
- **Gemini medium — `pathlib.Path`:** DECLINED. Premise ("stdlib supports path-like") is false —
  stdlib + oracle + purexml all raise the identical `AttributeError` on a `Path`; accepting it
  would diverge from the oracle. Pinned as deliberate parity (`test_path_object_matches_oracle_rejection`).

## Freeze note
The minidom + common surface is **STABLE-track** at 1.0 (mirrors a frozen reference, like
ElementTree). The `forbid_*` semantics and exception types match defusedxml exactly.

## Verdict
**Compliant.** `purexml.minidom` + `purexml.common` implemented per the approved RFC; oracle
parity (allow + block) proven, no-fetch verified on the new DOM surface incl. the F2 edge,
builder cleanup brought to the ElementTree refcount guarantee; four-leg run with the one real
PR-bot finding fixed and the false one grounded + declined. CI green 3.10–3.13. Ready to merge.
