# STACK.md — purexml

The canonical record of purexml's language, runtime, dependencies, and build/CI
shape. (Forked from the russalo universal template, which shipped Python+Go
scaffolding side-by-side; the Go half was deleted when purexml chose Python.)

## Language & runtime

- **Python, CPython ≥ 3.10** (PyPI floor `requires-python = ">=3.10"`).
  PyPy-portable. The floor is **CI-grounded** — the test matrix runs 3.10/3.11/
  3.12/3.13 on every push, so the declared floor is verified, not asserted.
- **Why 3.10 and not higher:** purexml must never become a consumer's binding
  Python floor (target spec §4). file-observer's real floor is ~3.10; the src
  uses only long-stable stdlib, so 3.10 is safe. Lowering further (≥3.8 is
  feasible per the spec) is deferred — untested here, and 3.10 already clears the
  anchor consumer.
- **pyexpat assumption:** the hardening is built on CPython's stdlib `expat`
  (`xml.parsers.expat`). A runtime *without* pyexpat (IronPython/Jython) would
  need a separate code path and is **out of scope** (no .NET/JVM consumer).

## Dependencies

- **Runtime: ZERO.** Standard library only — `xml.parsers.expat` +
  `xml.etree.ElementTree` (`TreeBuilder`, `ParseError`). This is a hard contract
  (target spec §4); a `src/`-level import of any third party is a test failure
  (`tests/test_misc.py::test_no_runtime_dependency_on_defusedxml`).
- **Dev/test: `pytest` + `defusedxml`.** `defusedxml` is the **oracle** purexml
  is validated against — never a runtime dependency, never imported under `src/`.
  Declared in `pyproject.toml` `[project.optional-dependencies].dev`.
- **Opt-in fuzz: `atheris`** (`[fuzz]` extra). Coverage-guided differential
  fuzzing only (`fuzz/`), on-demand — heavier tooling (clang/libFuzzer), so it is
  NOT in the always-run `[dev]` set or CI. Dev-only; never shipped, never under
  `src/`.

## Source layout

- `src/purexml/` — the `src` layout (not a flat package) is load-bearing: it
  forces an explicit editable install (`pip install -e .`) and prevents accidental
  import of the working tree. Modules: `__init__.py` (top-level re-exports),
  `ElementTree.py` (the canonical `purexml.ElementTree` namespace mirroring
  defusedxml), `_parser.py` (the expat-based engine — `XMLParser` + `fromstring`/
  `parse`/`iterparse`/`fromstringlist`), `errors.py` (exception hierarchy),
  `limits.py` (opt-in structural-DoS caps — `Limits`/`RECOMMENDED_LIMITS`, v0.4; the
  shared `_LimitCounter` accounting is reused by minidom + sax as of v0.14),
  `_expat_security.py` (opt-in libexpat version awareness + `security_report()`
  posture API, v0.5), `__main__.py` (the `python -m purexml` posture CLI, v0.7 —
  the package's one I/O boundary), `py.typed` (PEP 561 marker, v0.8 — the package ships
  its annotations). The public surface is type-annotated (v0.8); `from __future__ import
  annotations` keeps them lazy/runtime-inert.
- `tests/` at repo root, plain `pytest` (no `tests/__init__.py` — flat layout so
  `conftest.py` imports cleanly). See **Architecture** in `CLAUDE.md`.
- `fuzz/` at repo root — the opt-in Atheris coverage-guided harness (dev-only,
  not collected by pytest). The committed equivalence artifact is `docs/EQUIVALENCE.md`.

## Commands / dev environment

```bash
python -m venv .venv && . .venv/bin/activate   # .venv is gitignored
pip install -e ".[dev]"                         # pytest + defusedxml oracle
python -m pytest tests/ -q
```

Primarily a library (`purexml.fromstring(text)` etc.). A small read-only posture CLI
exists: `python -m purexml` (+ `--json` / `--check [--min-expat]` / `--version`, v0.7).

## CI

`.github/workflows/tests.yml`: two jobs, tag-pinned actions (`actions/checkout@v6`,
`actions/setup-python@v6`) —
- **`lint`** (single Python): `ruff check src/ tests/ fuzz/ tools/` (default rules) +
  `mypy` (typecheck the annotated surface — **`--strict`** since v0.8.1). Both
  version-independent — run once.
- **`test`** (matrix over Python 3.10–3.13, grounds the floor): `pip install -e ".[dev]"`
  then `python -m pytest tests/ -q --cov=purexml --cov-fail-under=90` — the coverage floor
  (currently ~94%) is enforced on every Python.

Dev tooling (in the `[dev]` extra): `pytest`, `defusedxml` (oracle), `ruff`, `pytest-cov`, `mypy`.
Tag-pinning (vs digest-pinning) is the right tradeoff for a pure-Python project on a small
action surface.

## Packaging / distribution

**Deferred to v1.0.** The vendor-vs-first-party adoption model — and with it PyPI
publishing, claiming the `purexml` name, and the license — is deliberately
unmade until v1.0 (see `CLAUDE.md` *Known decisions* and
`scratch/packaging_and_naming_notes.md`). Until then purexml ships as the
`src/purexml/` package in the private repo only; a vendorable single-file
amalgamation, if wanted, comes at the 1.0 adoption decision.

---

## The two-tripwire review guard (universal russalo convention)

purexml participates in the **four-leg decorrelated review apparatus** (in-house
swarm + Gemini cross-model + corpus sweep + PR bots). The kit lives at
**`/srv/projects/review-kit/`**; per-project adapters live in this project's
gitignored `scratch/review/`. Two safety tripwires gate the write-capable (yolo)
leg:

1. **`.review-canonical` marker** at the repo root (empty, committed). The yolo
   review wrappers refuse to run anywhere this marker is found at cwd/ancestor —
   protecting the canonical tree from a write-capable agent.
2. **Snapshot-root backstop.** `_review_guard.sh` also refuses to run outside
   `REVIEW_SNAPSHOT_ROOT` (default `/tmp`), so even without the marker the yolo
   agent can only write into the disposable snapshot area.

## The .gitignore stack toggle

The shipped `.gitignore` is the Python section (Go section deleted): editor
files, `.env`, `.claude/settings.local.json`, `scratch/`, `/tmp/`,
`__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.venv/`, `dist/`, `build/`,
`*.egg-info/`, `.coverage`, `htmlcov/`. The local `.venv` and the entire
`scratch/` tree (working notes, review adapters, corpus sweep, measure-first
findings) are gitignored — confirm before committing that neither appears in
`git status`.
