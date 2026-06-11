# STACK.md — language-variant adaptations for {{project_name}}

This template ships scaffolding for **both Python and Go side-by-side** so
a new project can pick its stack and delete the other half. The russalo
ecosystem's *process* conventions (review apparatus, scratch/, HISTORY.md,
PUBLIC_CONTRACT.md, the CLAUDE.md agent-instructions file) are
language-agnostic and stay in place regardless. This file documents what
to keep, what to delete, and which CI shape to use.

> Replace `{{project_name}}` everywhere with your project's short name.
> Keep it lowercase + hyphen-free — it becomes the Python import name
> and/or the Go binary name.

## What this template ships by default

| Slot | Python boilerplate | Go boilerplate |
| --- | --- | --- |
| Manifest | `pyproject.toml` | `go.mod` |
| Source layout | `src/{{project_name}}/` | `cmd/{{project_name}}/main.go` + `internal/` |
| Task runner | direct `pytest` / `pip install -e .` | `justfile` |
| CI workflow | `.github/workflows/tests.yml` (tag-pinned `@v6` actions) | `.github/workflows/ci.yml` (digest-pinned actions) |
| Lint | (none default) | `.golangci.yml` |
| gitignore | Python section active by default | Go section commented out — uncomment when adopting |

Pick one stack, delete the other. The shared scaffolding (CLAUDE.md,
docs/, scratch/, .review-canonical, HISTORY.md, etc.) stays put.

---

## Python

**pyproject.toml shape.** PEP-621 `[project]` table, `requires-python =
">=3.12"`, optional-deps named by purpose (e.g. `dev = [...]`), setuptools
build-backend. The top-level keys you'll edit are `name`, `version`,
`description`, `dependencies`, `[project.scripts]`, and `[project.urls]`.

**Source layout.** `src/{{project_name}}/` with an `__init__.py` and your
module files. The `src/` layout (rather than a flat `{{project_name}}/`
at repo root) is load-bearing — it prevents accidental import of the
working tree before `pip install -e .` and forces editable installs to be
explicit. CLI entry points wire through `[project.scripts]` into
`{{project_name}}.cli:main` (or wherever your `main()` lives).

**Testing.** `tests/` at repo root, plain `pytest` — no `setup.cfg` or
`pytest.ini` needed until you need it. Run `python -m pytest tests/ -q`.

**CI.** Use `.github/workflows/tests.yml`: `actions/checkout@v6` +
`actions/setup-python@v6` (tag-pinned, not digest-pinned — Python
projects move fast enough on the action surface that tag-pinning is the
right tradeoff). Install with `pip install -e ".[dev]"`, run
`python -m pytest tests/ -q`.

**Dependencies on system packages** (e.g. `libmagic1` for `python-magic`)
go in an `apt-get install` step BEFORE the pip install — the install step
needs the system library present, or the wheel build fails opaquely.

---

## Go

**Module path.** russalo Go modules live under `github.com/russalo/`:

```
module github.com/russalo/{{project_name}}
```

Even if the repo is private or the GitHub org is elsewhere, keep the
canonical `github.com/russalo/{{project_name}}` path — internal tooling and
the Blueprint KB assume it.

**Source layout.** `cmd/{{project_name}}/main.go` for the binary entry
point + `internal/` for packages, one package per concern
(`internal/server`, `internal/db`, etc.). Tests live alongside the code
(`*_test.go`), not in a separate `tests/` tree.

**Task runner.** `justfile` is the russalo-wide command runner. Standard
recipes: `just build`, `just test`, `just run`. Include a defensive
`export PATH := ...` line at the top of the justfile so recipes resolve
the right toolchain in non-interactive shells (cron, CI, sudo, deploy
hooks). A real deploy-no-op was caused by exactly this subshell-PATH
issue — `just deploy` succeeded but ran a stale binary because `PATH`
was unset and the wrong `go`/`docker` was on the fallback path. Without
this line, the class recurs.

**CI.** Use `.github/workflows/ci.yml`: lint + test jobs,
**digest-pinned actions** (`actions/checkout@<sha>  # v4.3.1` form),
`go-version-file: go.mod`, build cache enabled. Go projects are more
cgo-/toolchain-sensitive than Python, and a silent action update can
break a release path — digest pinning is the conservative default.

**golangci-lint.** Ship `.golangci.yml` with `install-mode: goinstall` in
the CI step — this is **load-bearing**, not stylistic. The prebuilt
golangci-lint binary is compiled against a specific Go version and will
refuse to lint a module that targets a newer Go in `go.mod`.
`install-mode: goinstall` builds it from source with the runner's
toolchain, avoiding the mismatch.

---

## Node (placeholder)

TBD. When a russalo Node project ships, lift its `package.json` shape,
its task-runner choice (likely `npm run` or `just`), and its CI workflow
shape into this section. Slot reserved.

---

## Rust (placeholder)

TBD. Same as Node — first russalo Rust project to ship gets to document
the conventions here. Slot reserved.

---

## The two-tripwire review guard (universal)

Regardless of language, every russalo project participates in the
**four-leg decorrelated review apparatus** (in-house swarm + Gemini
cross-model + corpus sweep + PR bots). The kit lives at
**`/srv/projects/review-kit/`**; per-project adapters live in this
project's gitignored `scratch/review/`.

Two safety tripwires gate the **write-capable (yolo) leg** of the review
apparatus, and both are universal russalo conventions:

1. **`.review-canonical` marker file at the repo root.** Empty file,
   committed. Sourced from review-kit's `_review_guard.sh`: if a review
   tool finds this marker at cwd or any ancestor, it refuses to run.
   Protects the canonical working tree from a yolo agent writing into it.
2. **Snapshot-root backstop.** `_review_guard.sh` also refuses to run
   anywhere outside `REVIEW_SNAPSHOT_ROOT` (default `/tmp`) — so even if
   the marker is missing, the yolo agent can only ever write into the
   disposable snapshot area.

Drop an empty `.review-canonical` at the repo root the moment you fork
this template. The review-kit script does the rest.

---

## The .gitignore stack toggle

The shipped `.gitignore` covers **both Python and Go**. Layout:

- **Universal section** (always active) — editor files, .DS_Store, .env,
  `.claude/settings.local.json`, `SCRATCH.md`, `scratch/`, `/tmp/`.
- **Python section** (active by default) — `__pycache__/`, `*.py[cod]`,
  `.pytest_cache/`, `.venv/`, `dist/`, `build/`, `*.egg-info/`,
  `.coverage`, `htmlcov/`.
- **Go section** (commented out) — `/bin/`, `/{{project_name}}`,
  `vendor/`, `*.exe`. Uncomment when adopting Go; delete the Python
  section if you're not using Python.

The leading slash on `/bin/` and `/{{project_name}}` is load-bearing —
without it, the patterns would also match `cmd/bin/` or a `{{project_name}}/`
package directory. See the inline comment in the gitignore.
