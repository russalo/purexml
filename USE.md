# Using this template

Procedural doc for spinning up a new project. Two ways to do it: the
deploy script (recommended) or manual copy. The script bakes the manual steps
into one command and substitutes placeholders / strips the other stack / runs
`go mod init` / optionally `git init` — but the manual path is here too for the
"I want to see what's happening" case.

## Recommended path — the deploy script

The template root carries `new-project.sh`. From anywhere on the node:

```bash
/srv/projects/pkplab/project-template/new-project.sh <target-dir> [--lang LANG] [--name NAME] [--git]
```

Or symlink it onto your PATH once:

```bash
ln -s /srv/projects/pkplab/project-template/new-project.sh ~/.local/bin/new-project
# then:
new-project /srv/projects/foo --lang go --git
```

`--lang` accepts:
- `python` — Python boilerplate only (pyproject.toml, src/, tests/, Python CI)
- `go` — Go boilerplate only (cmd/, internal/, justfile, Go CI, `go mod init` ran for you)
- `all` — both stacks side-by-side (default; you pick later via STACK.md cutover)
- `none` — docs + scratch + .gitignore + .review-canonical only (language-agnostic skeleton)

The script:
- Strips the other stack's files when `--lang` selects one
- Renames `src/example` → `src/<name>` (Python) and `cmd/app` → `cmd/<name>` (Go)
- Substitutes `purexml` everywhere it appears
- Drops the template-development scratch (`scratch/notes.md`, `scratch/blog_go_*.md`)
- Removes itself from the spawned project (so it doesn't pollute downstream)
- Optionally `git init` + initial commit with `--git`

After the script: read `USE.md` (this file) for the per-project follow-up steps,
then `CLAUDE.md` for the agent-instruction baseline.

## Manual path (if you want the explicit steps)

### Step 1 — Copy the template

```bash
cp -r /srv/projects/pkplab/project-template /srv/projects/<owner>/<name>
cd /srv/projects/<owner>/<name>
rm new-project.sh   # the deploy script doesn't belong in the spawned project
rm scratch/notes.md scratch/blog_go_*.md scratch/draft_to_*.md  # template-dev scratch
```

The template ships a `.review-canonical` marker at the repo root — keep it
there (it tells the yolo-mode Gemini review wrappers to refuse to run in this
tree). See **Step 6**.

## Step 2 — Pick your stack

See `STACK.md` for the language-variant guide. Two stacks are pre-wired:

### Python

```bash
rm -rf cmd internal justfile .golangci.yml go.mod go.sum
# Open .gitignore: uncomment the Python section, delete the Go section.
mv src/example src/purexml
# Open pyproject.toml — set name, description, dependencies.
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

### Go

```bash
rm -rf pyproject.toml tests src
# Open .gitignore: comment out the Python section, uncomment the Go section.
mv cmd/app cmd/purexml
go mod init github.com/russalo/purexml
go mod tidy
```

## Step 3 — Fill in the placeholders

Walk these files and replace `purexml` / TODO blocks / «...» blocks
with project specifics:

- `README.md` — what it is, install, basic use. Public-facing.
- `CLAUDE.md` — agent instructions. Project pillars, architecture, known
  decisions. This is the file Claude reads first; spend time here.
- `SECURITY.md` — threat model, reporting path, supported versions.
- `CONVENTIONS.md` — internal naming, version-bump rules, document promotion
  paths. Grows as the project gathers terminology.
- `PUBLIC_CONTRACT.md` — consumer-facing stability commitments. Empty until
  v1.0 (binding from v1.0 onward).
- `LIMITATIONS.md` — what this tool does NOT do, and what's deferred.

## Step 4 — Set up the review apparatus

The four-leg decorrelated review apparatus is documented at
`/srv/projects/review-kit/` (Russell-owned canonical) and described in
`scratch/review/README.md` (per-project copy, shipped with the template). The
template ships only the project-specific **adapters**, not the wrapper scripts.

Edit:

- **`scratch/review/auditor_GEMINI.md`** — fork of the skeleton from
  `/srv/projects/review-kit/auditor_GEMINI.skeleton.md`. Fill in:
  - *What this project is* — one paragraph; trust boundary; what counts as a
    breaking change. Misreading this is the #1 source of bad findings.
  - *Severity rubric blocker definition* — tune to your trust model.
  - *Language footguns* — keep the relevant section (Go or Python), delete the
    other (or keep both if polyglot).
  - *Per-project hunt list* — starts empty; grow it as real review rounds
    catch real bugs.

The wrapper scripts (`gem.sh`, `gem-oauth.sh`, `gem-review.sh`,
`_review_guard.sh`) are **referenced from the canonical**, not copied —
`/srv/projects/review-kit/gem-oauth.sh -p "..."` rather than a local copy.

## Step 5 — First commit + HISTORY.md

```bash
git init -b main
# Edit HISTORY.md: replace the seed row with your v0.1.0 row.
git add -A
git commit -m "v0.1.0 — initial scaffold from project-template"
```

`HISTORY.md` is the running version index. Every release (minor or patch)
gets one row. RFC-bearing minors link their RFC; patches link the
HISTORY entry itself (the no-RFC-for-patches rule: RFCs for minors+, HISTORY
for patches).

## Step 6 — Verify `.review-canonical`

```bash
ls -la .review-canonical
```

This empty file at the repo root is the **primary tripwire** for the
write-capable Gemini review extensions (`gem-review.sh` via
`/srv/projects/review-kit/`). When present, the wrappers refuse to run — they
require a disposable `/tmp` snapshot instead. The template ships the file;
don't delete it.

If you need to run a whole-codebase red-team:

```bash
cp -r src tests /tmp/purexml_audit && cd /tmp/purexml_audit
git init -q -b main && git add -A && git commit -qm snapshot
/srv/projects/review-kit/gem-review.sh -p "/maestro:security-audit Proceed AUTONOMOUSLY using Approach 2 …"
```

The snapshot has no `.review-canonical`, so the guard allows yolo writes —
isolated from the real tree.

## Step 7 — First RFC (when you're ready for a minor)

Patches go in `HISTORY.md` only. **Minors and above need an RFC.** Draft at:

```
docs/v<X.Y.Z>_RFC_Specification.md
```

Follow the conventions in `CONVENTIONS.md`:

- Falsify-first — build the adversarial corpus / repro BEFORE writing the fix.
- Measure-first — for performance/parser/parallelism work, prototype + measure
  *before* committing to a decision (a `scratch/measure_*.py` script kept in
  the repo is the conventional shape).
- State the contract: what moves (SCHEMA / LOGIC / version), what doesn't, and
  what the falsifiable test is.

After ship, archive prior RFCs to `docs/archive/<series>/` and link from
`HISTORY.md`.

## Hand-off: the spawned Claude's first session

When a Claude Code instance first opens the spawned project, its FIRST action
should be reading `CLAUDE.md`'s **Operating contract** and running the
**First-session bootstrap** checklist there — above all the **chatlog-home
transition** (`/srv/projects/pkplab/chatlogs/<project>/` subdir + `PROJECTS.txt` line). That
step is one-time and easy to silently skip; skipping it loses the project's
session history. Don't assume it ran — verify the subdir exists.

The Operating contract also carries the most important thing about this
template: **it's a starting point.** The gates (four-leg review, RFC → spec →
implement, lane discipline) are the operational floor. Evolving them into a
workflow that fits *this* project is normal and expected — as long as the
evolution is a conscious, recorded decision, not a silent slide back to
generic defaults. The contract names that distinction explicitly, because a
prior instance regressed by sliding rather than deciding.

---

**Supplementary examples.** For worked examples of the patterns this template
ships, look at existing projects on the node (scanner, blog, tether). They
each demonstrate the conventions in production. Treat them as illustrations,
not as the canonical source — this template is the canonical source.
