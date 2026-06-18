# COMPLIANCE — purexml v0.8.0

Audit of v0.8.0 against the approved spec
[`v0.8.0_RFC_Specification.md`](v0.8.0_RFC_Specification.md). Environment: CPython
3.12.3, libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). PR
[#21](https://github.com/russalo/purexml/pull/21), branch `v0.8.0`. Suite: **179 passed,
1 gated-skip.**

## Theme
Ship types: annotate the public surface + a PEP 561 `py.typed` marker so consumers'
type-checkers use purexml's own types instead of `Any`. **No runtime/parse change.**

## §2 Capability + §5 design (resolved to the approved leans)

| Req | Implementation | Status |
|---|---|---|
| Public surface annotated, accurate (no Any-washing) | ElementTree family, `XMLParser`, `security_report`/`SecurityReport`/`as_dict`, expat API, errors, `__main__.main` | ✅ |
| `SecurityReport` fields typed for consumers | class-level field annotations — `reveal_type` confirms `tuple[int,...]`/`Mapping[str,str]`/… not `Any` | ✅ |
| `source` accepts filename/bytes/path/file | `str \| bytes \| _PathLike \| IO[Any]` (structural `Protocol`, no `os` import) | ✅ |
| `py.typed` shipped (PEP 561) | marker + setuptools package-data; verified in the wheel; `test_py_typed_marker_shipped` | ✅ |
| `mypy`-clean + CI typecheck job (defer `--strict`) | `[tool.mypy]` config; CI `lint` job runs `mypy` | ✅ |
| Verbatim `_setevents` mirror preserved | `# type: ignore[misc]` on the redefinitions (not renamed) | ✅ |
| `types: mypy` badge | README candidate | ✅ |

## §6 Acceptance bar

| Req | Evidence | Status |
|---|---|---|
| No runtime/parse change; mirror byte-equivalent | sweep **372/0**; suite green; `__future__` annotations are lazy/inert | ✅ |
| `mypy` clean, CI-enforced | `Success: no issues found in 7 source files`; CI `lint` job runs `mypy` | ✅ |
| `py.typed` shipped in the wheel | `pip wheel` inspection confirmed `purexml/py.typed` present | ✅ |
| Public signatures accurate (no Any-washing) | in-house + PR-bot review confirmed; the `Any`s (iterparse/close/as_dict) reflect genuine variance | ✅ |
| no-I/O guard holds | `typing`/`__future__` added to allowlist (pure, lazy); FORBIDDEN check unchanged; `test_no_io` green | ✅ |

## Four-leg review — run (with one tooling caveat, recorded)

| Leg | Result |
|---|---|
| 1 — in-house | ✅ clean — accurate annotations, every `# type: ignore` legitimate (verbatim mirror / structural-drop-in), runtime-inert, parse path untouched. |
| 2 — Gemini cross-model (`gem.sh`) | ⚠️ **unavailable** — gemini CLI individual tier deprecated (`IneligibleTierError`). Shared review-kit breakage; cross-model coverage provided by leg 4's `gemini-code-assist` bot instead. Recorded; flagged for review-kit repair. |
| 3 — empirical sweep | ✅ **372/0** — mirror byte-identical. |
| 4 — PR bots (Codex + Gemini Code Assist) | ✅ **5 findings, all real, all fixed** (commit 5c51bae) — the two substantive ones (SecurityReport fields `Any`; `source` too narrow) materially improved the typed surface. |

### Findings dispositions — grounded; nothing declined
- **Pre-open (legs 1, 3):** clean.
- **PR-bot (leg 4):** SecurityReport class-level annotations (verified via `reveal_type`);
  `_PathLike` Protocol widening `source`; `dict[str,str]` for `_names`/`entity`.
- Codex P2 ×2 + Gemini high ×2 + medium — all addressed.

## Freeze note
The public *type signatures* freeze with the mirror surface at 1.0 (a wrong-then-frozen
signature would be a 2.0-class mistake — captured in CONVENTIONS' API table). The
`SecurityReport`/CLI/JSON shapes remain PROVISIONAL.

## Verdict
**Compliant.** Types shipped per the approved RFC; no runtime/parse change, mirror proven
byte-equivalent (372/0); mypy-clean + CI-gated; `py.typed` verified in the wheel; PR-bot
findings grounded and fixed (typed surface verified accurate via `reveal_type`). Leg-2
unavailability recorded with cross-model coverage preserved via leg 4. CI green 3.10–3.13.
Ready to merge.
