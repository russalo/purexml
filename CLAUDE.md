# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

## What this is

**TODO: Replace with a one-paragraph description of the project.** Anchor on the
*role* the project plays (observation layer / web server / job runner / library
for X), not the surface (it's "Go" / it's "Python"). The surface lives in
`STACK.md`. Keep it short — agents read this first, every session.

## Lane discipline

The russalo ecosystem runs multiple projects on the same node. This project's
Claude instance operates inside a documented lane. **Role map:**

> **Tailnet CONTROLS** infra. **Blueprint RECORDS** the canonical reference.
> **This project = neither.** It owns its own code, its own records (for its
> own reference), and reports state up.

### Your lane (this project)

- **Read + write freely** within this project's directory (`$PWD` and below).
  That includes `scratch/` (gitignored working notes), `docs/` (promoted
  outputs), and the project's own state / data dirs.
- **Read + write** within `/srv/projects/pkplab/chatlogs/<this-project>/` —
  the unified per-project Claude session-jsonl tree (documented exception).
- **You may store your own records** for the project's own reference —
  decisions, state snapshots, integration notes, anything the project itself
  needs to function or remember. Blueprint is the canonical *cross-project*
  reference; per-project records inside this directory are yours.
- **Read-only** everywhere else on the node unless Russell authorizes a
  specific write. Examples: other projects under `/srv/projects/`, the
  shared review-kit at `/srv/projects/review-kit/`, system config, user
  home outside `~/.claude/`.

### Tailnet's lane (NOT yours)

Tailnet Claude owns the **infra layer** — DNS, certs (Caddy), live-prod
services, systemd units at `/etc/`, firewall rules, Tailscale ACLs, SSH
config, host package upgrades, the workbench deployment shape. You do
**not** touch these. You also do **not** probe them to verify state —
read-only awareness is fine ("the workbench is at this port"), but
verifying an infra change is Tailnet Claude's call.

### Blueprint's lane (NOT yours)

Blueprint Claude owns the **ecosystem-level inventory** — the canonical
record of what runs where, which projects exist, cross-project
knowledge-docs at `blueprint.dev.russalo.com/api/inventory/`. Blueprint
is the *record of all reference*. Per-project records (the kind you keep
in *this* repo) are not in Blueprint's lane; they're yours. Cross-project
state — additions, subtractions, version-shipped, deprecations — IS in
Blueprint's lane.

Blueprint also records **host tooling** — for questions about what's
installed on the node (CLIs, language toolchains, services, version pins),
Blueprint's API is the canonical answer rather than `which`-discovery.
The short list of standard tooling is in **Host environment** (next
section); the live inventory lives in Blueprint.

### Implicit obligation: inform Russell so he can route

You have an active duty to **surface state changes** so Russell can route
them. Two channels:

1. **→ Tailnet (request)** — when this project needs an infra change (a
   port opened, a DNS record, a deploy unit hardened, a service
   redeployed). Draft the ask at `scratch/draft_to_tailnet_<date>.md`;
   surface it to Russell; wait for relay. Never direct-implement.
2. **→ Blueprint (state change)** — when this project's *cross-project
   state* changes (new version shipped, new public surface added, a
   dependency added, a feature added or removed that other projects might
   consume, deprecations, sunsets). Draft a
   `scratch/draft_to_blueprint_<date>.md` summary; surface to Russell;
   wait for relay (or for Blueprint Claude to pick it up via the
   workbench if applicable).

The obligation runs both ways: you inform up, and you act on relayed
information coming down. Don't sit on state changes hoping someone
notices.

### Cross-Claude communication

Other projects on the node have their own Claude instances. **You do not
message them directly.** The only paths:

1. **Through Russell** — write a `scratch/draft_to_<Claude>_<date>.md`,
   ask Russell to relay it.
2. **Through Tether** (when applicable) — the shared workbench / message
   layer at `/srv/projects/pkplab/tether/`, used for durable collaboration
   surfaces.

Never assume another Claude is reading the filesystem in real-time. Never
write to another project's `scratch/` or `docs/` to communicate.

When referencing Claude instances in conversation with Russell, **always
specify scope**: yourself (this instance), a named Claude (Blog Claude,
Blueprint Claude, Tailnet Claude…), all Claudes on this node, or Claudes
other than yourself. No bare "Claude Code does X" — Russell can't follow
which instance you mean.

### When unsure

Ask Russell. The cost of pausing for confirmation on a possibly-cross-lane
action is one round-trip; the cost of an unwanted touch (broken deploy,
ACL widened, dependency upgraded mid-flight, another project's state
mutated) is much higher. The defaults are: **read-only outside your lane,
ask before crossing, surface state changes promptly.**

## Host environment

This project runs on **origin-core** (the Linux host that anchors the
russalo.com ecosystem) inside the **russalo Tailscale tailnet VPN** —
the node is reachable only from tailnet-joined devices, not the open
internet. Public-facing services on origin-core sit behind Caddy (Tailnet
Claude's lane); everything else is tailnet-only.

> **Note:** if you're spawning this template for a project that does NOT
> live on origin-core, replace this section with the actual host context.
> The patterns below assume origin-core's ambient tooling.

### Standard ambient tooling

The russalo node ships these tools standard. Use them by name from any
shell session; they're not project-installed.

| Tool | Purpose | Where to learn more |
|---|---|---|
| `gh` | GitHub CLI — PRs, issues, releases, gh-actions. Auth'd as `russalo`. | Blueprint inventory + `gh --help` |
| `git` | Source control. The russalo GitHub org is the canonical remote for most projects. | — |
| `just` | Task runner (russalo standard). Replaces Make; see this project's `justfile`. | `just --list` |
| `gemini` (CLI) | Gemini CLI for the cross-model review leg. Two surfaces: API-key (flash, durable) and OAuth (pro). | Blueprint `gemini-review-infra` doc |
| `gem.sh` / `gem-oauth.sh` / `gem-review.sh` | Wrapper scripts at `/srv/projects/review-kit/` that paper over the gemini CLI's gotchas (stale env key, untrusted-folder hang, approval-mode differences). | `/srv/projects/review-kit/README.md` |
| `file-observer` | russalo's PyPI'd observation layer (file → manifest). Install via `pip install file-observer[pdf,watch]` if your project needs deterministic file metadata. | https://pypi.org/project/file-observer/ |
| Language toolchains | Python 3.12+, Go (current stable), Node, etc. — versions tracked in Blueprint. | Blueprint inventory |

### Documented service references (read-only awareness)

These services run on the node. You can **mention** them in conversation
("the workbench is at port 8801"), but you do **not** probe them to
verify state — that's Tailnet Claude's lane.

| Service | Surface | Notes |
|---|---|---|
| Workbench hub | `http://origin-core:8800` (tailnet) | Shared Tether workbench across projects |
| Per-project workbench instance | `http://origin-core:880N` (tailnet, per project) | Spawned via `tether/hub.py` |
| Blueprint dev | `https://blueprint.dev.russalo.com/api/inventory/` (tailnet) | Canonical ecosystem record |

### When tooling drifts from what's listed here

If you discover a tool that's installed but not on this list, or a tool
listed here that isn't present, that's a **state change Blueprint needs
to know about**. Draft to `scratch/draft_to_blueprint_<date>.md` and
surface to Russell — same channel as any other state-change-up.

## Spec

This project follows the russalo **RFC-for-minors-only** rule:

- **Minor and major releases** (vX.Y.0, vX.0.0) land an approved RFC at
  `docs/v{X.Y.Z}_RFC_Specification.md` *before* implementation, and a matching
  compliance report at `docs/COMPLIANCE-v{X.Y}.md` before merge.
- **Patch releases** (vX.Y.Z, Z>0) do **not** get an RFC. The full narrative
  lives in `HISTORY.md` only. Patches are bug fixes, red-team hardening,
  determinism corrections — anything where the design was already approved in
  the parent minor's RFC.

The reason: RFCs are expensive (review, approval, compliance). Patches that
fix bugs in an already-approved design don't earn that overhead; their record
belongs in the version history, not a parallel spec doc.

One-line bullets per version (newest first; copy the shape from
[`HISTORY.md`](HISTORY.md)):

- **v{X.Y.Z}** — TODO: one-line summary of the release. Reference the RFC for
  minors, or just "_HISTORY only_" for patches. Note version-axis changes
  (e.g. SCHEMA 1.x → 1.y; LOGIC unchanged).

## Stack

See [`STACK.md`](STACK.md) — the canonical record of language, runtime,
dependencies, and any template-variant adaptations.

## Commands

Stack-dependent. Both shapes are baked into this template; delete the one you
don't use:

- **Go projects:** task runner is **`just`** (russalo-wide standard). List
  recipes with `just`; run with `just <name>`. See [`justfile`](justfile).
- **Python projects:** install + run via [`pyproject.toml`](pyproject.toml).
  Typical shape: `pip install -e ".[dev]"` then `{{cli_name}} --help` and
  `python -m pytest`.

If the project grows commands the runner doesn't cover, document them in
`STACK.md` or a `Commands` section here — not in tribal knowledge.

## Architecture

**TODO: Replace with a short tour of the codebase.** One paragraph per major
seam (entrypoint, request flow, data layer, background work). Reference
modules by relative path. Agents use this to orient before reading code.

## Known decisions

A running list of things future-you (and future agents) will want to know
*before* changing related code. Add a one-line bullet whenever a non-obvious
choice gets locked in — anti-pattern is finding the decision only by `git
blame`.

- TODO: First decision goes here. (Pattern: "**X** — why we picked it over Y.")
- TODO: Second decision goes here.
- TODO: ...

## Test fixtures

Tests live in `tests/`. Fixtures (sample inputs, golden outputs, edge cases)
live alongside them — typically `tests/fixtures/`. Run the full suite via the
stack's standard command (`just test` for Go, `python -m pytest` for Python).
The exact test count moves with every PR, so this doc doesn't pin it.

## Review apparatus

This project uses the **four-leg decorrelated code review** apparatus that
the russalo ecosystem has converged on. The originating principle: *a
reviewer's value is its decorrelation from the author.* Builder bias applies
to the AI too — review must come from where the author didn't think.

The four legs (run all on minors+; subset on patches per scope):

1. **In-house multi-agent swarm** — finder angles × candidates → verify →
   ranked findings. Same model, decorrelated *perspectives*.
2. **Gemini cross-model** — different model family. Two modes: inline prompt
   (`gem.sh` / `gem-oauth.sh`, read-only, pre-PR diff review) and native
   review skills (`gem-review.sh` → `/code-review`,
   `/maestro:security-audit`, yolo-mode + `/tmp` snapshot guarded, for
   whole-codebase red-teams).
3. **Repo-clone audit + empirical sweep** — clean-room clone; deterministic
   sweep vs a baseline.
4. **PR bots** — Codex / Gemini Code Assist / Copilot on PR open. External.

**Canonical tooling:** [`/srv/projects/review-kit/`](file:///srv/projects/review-kit/)
is the Russell-owned shared kit (lift-and-adapt source). Per-project copies
live in `scratch/review/` along with the project's auditor adapter (a
`auditor_GEMINI.md` filled in from `auditor_GEMINI.skeleton.md`), corpus
sweep harness, findings logs, and any project-specific overlays.

**Grounding rule (non-negotiable):** triage every cross-model / bot finding
against the real code before it counts. Construct the failing input, confirm
it's real, *then* fix. Models overstate severity and critique code they were
never shown.

A `.review-canonical` marker file at the repo root tells the yolo-mode review
wrappers that this is the canonical repo (not a `/tmp` snapshot). The marker
travels with the repo via git.

## Memory

`~/.claude/projects/<encoded-repo-path>/memory/` is the **per-Claude-instance**
memory layer — Russell's auto-memory across sessions for *this* instance of
Claude Code on *this* node. It is **not** project memory. Project memory
lives in:

- `scratch/` — gitignored working notes, working drafts, draft RFCs,
  pre-promotion observations (run state, fixture exploration, etc.)
- `docs/` — promoted, durable, version-tracked outputs (specs, compliance,
  conventions, contracts)

Promotion is one-way: `scratch/` → `docs/` once value emerges. See
[`CONVENTIONS.md`](CONVENTIONS.md) §3 (promotion path).

## Conventions

See [`CONVENTIONS.md`](CONVENTIONS.md) for naming rules, version-bump rules,
document promotion paths, and the project's tracking inventory (specialists,
namespaces, error codes, etc. — projects fill these in as they accumulate).

The version-bump rules in particular are load-bearing: this project (like all
russalo projects with a stable contract) carries **multiple independent
version axes** (release version, internal logic version, public schema
version) that bump independently. CONVENTIONS.md is where the rules for each
axis live.
