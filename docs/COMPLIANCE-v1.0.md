# COMPLIANCE — purexml v1.0.0 (the contract freeze)

Audit of v1.0.0 against the approved spec
[`v1.0.0_RFC_Specification.md`](v1.0.0_RFC_Specification.md). Environment: CPython 3.12.3,
libexpat 2.6.1, defusedxml 0.7.1 (dev/test oracle only). Suite: **372 passed, 1 gated-skip.**

## Theme
1.0 is a **governance/contract freeze on a validated codebase — not a feature release.** The
`defusedxml`-mirror surface is locked STABLE-to-2.0; the opt-in defense-in-depth stays
PROVISIONAL by design. **No `src/` parse-or-block code changes in this release** — the freeze
is version + binding-contract docs + a mechanical guard test. Ratified by Russell and the
file-observer steward (2026-07-07).

## §3 frozen surface — implemented + guarded

| Spec item | Where | Guard | Status |
|---|---|---|---|
| Module namespaces (`ElementTree`/`minidom`/`sax`/`expatreader`/`xmlrpc`/`common`) | `src/purexml/` | `test_public_contract.py::test_module_namespaces_present` | ✅ |
| Function signatures + `forbid_*` defaults + keyword-only `limits` | `_parser.py`, `minidom.py`, `sax.py` | `test_public_contract` (`_forbid_defaults`, surface tests) | ✅ |
| Defaults `forbid_entities=True`/`forbid_external=True`/`forbid_dtd=False` | `_parser.py` | contract test + `test_fo_contract` | ✅ |
| Exception hierarchy COMPLETE (`PureXMLError(ValueError)` ← 4 + `LimitExceeded` ← 3) | `errors.py` | `test_public_contract::test_exception_hierarchy_is_exactly_the_frozen_set` | ✅ |
| `common.DefusedXmlException is PureXMLError` | `common.py` | `test_public_contract::test_common_defusedxml_alias_frozen` | ✅ |
| `requires-python >= 3.10` floor (won't rise within 1.x) | `pyproject.toml` | `test_fo_contract::test_fo_5_python_floor_stays_3_10` | ✅ |
| `__version__` plain `str` | `__init__.py` | `test_public_contract` + `test_fo_contract` | ✅ |
| `Limits`/posture/version-assertion = PROVISIONAL (not pinned) | `PUBLIC_CONTRACT.md` §2.2 | (deliberately not frozen) | ✅ |

`PUBLIC_CONTRACT.md` filled + binding; `docs/v1.0.0_RFC_Specification.md` promoted +
ratified; version → 1.0.0 (pyproject, `__init__`, CONVENTIONS); classifier → Production/Stable.

## §6 acceptance bar (binding)

| Gate | Result |
|---|---|
| Full suite (CPython 3.12; CI matrix 3.10–3.13) | **372 passed, 1 skip** |
| New contract-freeze guard (`test_public_contract.py`) | **24 passed** |
| Coverage (`--cov-fail-under=90`) | pass (~94%) |
| `mypy --strict` | clean (12 files) |
| `ruff` (src tests fuzz tools examples) | clean |
| **Mirror untouched** — empirical sweep vs defusedxml oracle | **372 real inputs, 0 disagreements** |
| Build + `twine check` (sdist + wheel) | PASS — `purexml-1.0.0`, Production/Stable |
| libexpat currency | IN-SYNC (2.8.2) |

**No parse-or-block behavior change** — the mirror-untouched sweep (0 divergences) is the
evidence, not the assumption. LOGIC unchanged; SCHEMA n/a.

## Review legs (tier: governance/contract freeze — no `src/` parse change)

The security-load-bearing adversarial legs scale to the change: this release touches **no
parse code**, so the empirical sweep serves as the "mirror-untouched" proof, and the in-house
leg verifies the frozen contract *accurately matches the code* (signatures, defaults, exception
set enumerated in `test_public_contract.py` were grounded against `src/`).

- **Leg 1 (in-house)** — ✅ frozen surface grounded against `src/` symbol-by-symbol; the guard
  test encodes it.
- **Leg 2 (cross-model)** — n/a-scaled (no parse-or-block change; the contract text + version
  bump carry no adversarial parse risk). Recorded per the report-only/governance tier.
- **Leg 3 (empirical sweep)** — ✅ mirror-untouched, 0 divergences over 372 real inputs.
- **Leg 4 (CodeRabbit, on PR open)** — _(finalized before merge — see PR.)_

## Ratification
Ratified by Russell (all gating calls) + the file-observer steward (full sign-off, all four
points incl. the floor + `__version__` gap-check). See RFC §9 for the ratification record.

## Not in scope of this release
PyPI publication + claiming the `purexml` name — a separate, deliberate strategic step
(Russell's). The repo-side freeze (this) is independent of distribution.
