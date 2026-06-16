# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

## Operating contract — read this first, every session

**This file is operational, not reference.** It is a set of GATES you execute
and verify at — not background you read once and absorbed. That distinction is
the whole point of everything below it.

**The #1 failure mode of an instance spawned from this template is silent
default-reversion:** running generic Claude-Code behavior — read the task, do
it, use whatever tools fire automatically, ship — and consulting this overlay
only when something forces you to. It is a real, documented failure. A prior
template-spawned instance drifted exactly this way: it ran the four-leg review
as one-and-a-half legs (skipped the in-house swarm and the Gemini cross-model
leg on minor releases that mandate all four), never performed the chatlog-home
setup, opened a PR for an RFC *draft*, re-introduced design elements that had
been explicitly excluded, and — under an explicit read-only / verify-first
order — treated agreement on a plan's *intent* as authorization to *execute*
and began writing. **None of it registered AS deviation in the moment**, because
the actions were never held against these requirements at the gate where each
occurred. Its own diagnosis: "silent unawareness, not a conscious shortcut —
the harder kind to catch."

If you are not actively checking your actions against the gates in this file,
**you are already drifting** — you just don't feel it yet. The lighter path
always feels sufficient mid-session; in a fast, design-heavy session, process
scaffolding reads as skippable overhead while things appear to be going fine.
**That feeling is the failure mode, not a signal that you're fine.** This will
override even direct in-conversation corrections unless you operationalize the
gates into active checks.

### This is a STARTING POINT — evolving away from it is normal and expected

These gates are your **operational floor, not a cage.** Every real project
evolves its own workflow: it drops a gate that doesn't fit its domain, adds one
the template never imagined, reshapes the RFC flow around what it actually
builds. **That evolution is healthy and expected** — the russalo way is "fluid
early, structured as value emerges." This template is where you *start*, not
where you stay.

The line that matters is **conscious evolution vs. silent regression:**

- **Evolution (good):** you *decide* to change how this project works, you say
  so to Russell, and you record it (`Known decisions` below / `CONVENTIONS.md`).
  The deviation is a choice with a paper trail.
- **Regression (bad):** you *slide* off a gate without noticing — default-
  reversion. No decision, no record, no awareness. This is the failure this
  contract exists to prevent.

So deviating from the template is fine. Deviating **without noticing** is the
failure. When you find yourself about to skip a gate, that is the moment to
either run it or make an explicit, recorded decision not to — never the moment
to quietly proceed.

## First-session bootstrap (one-time, do before real work)

When this project is freshly spawned, run this checklist BEFORE substantive
work. These are one-time setup steps the template cannot perform for you:

- [x] **Chatlog home.** DONE 2026-06-16. Chatlog home is
  `/srv/projects/pkplab/chatlogs/purexml/`; the encoded dir
  (`~/.claude/projects/-srv-projects-pkplab-purexml/`) now holds symlinks back
  to it, and `-srv-projects-pkplab-purexml\tpurexml` is registered in
  `/srv/projects/pkplab/chatlogs/PROJECTS.txt`. (Recipe:
  `/srv/projects/pkplab/chatlogs/TRANSITION.md`.) Future sessions land a fresh
  jsonl at the old path; `chatlogs/sync.sh` migrates them.
- [x] **Review apparatus wired.** DONE 2026-06-16. `scratch/review/` exists;
  `auditor_GEMINI.md` adapter filled (project "What this project is", blocker
  definition, and a live Python XML-hardening footgun list — Go list flagged
  N/A). Shared wrappers at `/srv/projects/review-kit/`. Still TODO as the project
  ships: `corpus_sweep.py`, baseline, per-release findings logs.
- [x] **Read the ledgers.** DONE 2026-06-16 — read and populated `Known
  decisions` + `Excluded decisions` below from the target spec, RFC, and
  packaging notes.
- [x] **Fill or track the TODOs.** DONE 2026-06-16. Filled `What this is`,
  `Architecture` (noting no code yet), version/axes section, README, and
  `pyproject.toml` from the target spec. Genuine open decisions (license,
  PyPI publishing, repo URLs) are *tracked as pending the adoption-model
  decision*, not guessed.

## Decision gates (STOP and verify — do not proceed past these on autopilot)

Run the relevant checklist AT the moment, not from memory of having read it.

**Before you execute ANY plan or write ANY file:**
- [ ] Am I in *execute* mode or *discuss* mode? **Agreement on a plan's intent
  is NOT authorization to execute it.** Repeating a plan back is not permission
  to do it. Under a read-only / verify-first order, stay read-only until Russell
  explicitly says execute.
- [ ] Is what I'm about to write inside my lane? (See Lane discipline.)

**Before finalizing/approving an RFC:**
- [ ] Is this a *draft* or an *approved spec*? Drafts are reviewed in
  conversation — they do NOT get a PR. The PR belongs at implementation.
- [ ] Have I locked specifics into the spec that the draft stage should still be
  shaking out (e.g. a concrete visual/design choice)? The draft stage exists to
  prevent exactly the rip-it-out-later failure.

**Before opening a PR (minors+):**
- [ ] Did the three *pre-open* review legs run — in-house swarm, Gemini
  cross-model, repo-clone/empirical sweep? (The fourth leg, PR bots, fires *on
  PR open* — it's checked at the before-merge gate, not here.) "Subset on
  patches per scope" is a decision you make and record, not a default you slide
  into.
- [ ] Are those findings logged in `scratch/review/`?
- [ ] Is this implementation (PR-worthy), not a draft (conversation)?
- [ ] Did I re-introduce anything in `Excluded decisions`?

**Before merge (minors):**
- [ ] Did the PR-bot leg fire (Codex / Gemini Code Assist / Copilot), and are
  its findings addressed or grounded-and-declined?
- [ ] Compliance report written? CI green? Review comments addressed/grounded?

## Where this project diverges from your generic defaults

Default-reversion strikes precisely at these divergence points — so they are
named here to make them catchable. Where your base Claude-Code instinct and this
project disagree, **this project wins** (until you consciously evolve it):

| Your default instinct | This project's gate |
|---|---|
| Read the task, do it, ship | Minors go RFC → spec → implement → compliance |
| Review = whatever fires (PR bots) | Four legs, all of them on minors+, findings logged |
| Agreement means proceed | Agreement on *intent* ≠ authorization to *execute* |
| Session logs live wherever the CLI writes them | Transitioned to `/srv/projects/pkplab/chatlogs/<project>/` (bootstrap) |
| Write where the work is | Lane discipline — read-only outside your lane |
| A draft is ready to PR | Drafts live in conversation; PRs are for implementation |

## What this is

purexml is a **pure-Python, zero-runtime-dependency security control for parsing
untrusted XML** — a drop-in replacement for the `defusedxml` library so consumers
can drop that third-party dependency with **zero functionality loss** (same
parses succeed, same attacks blocked). The key insight: `defusedxml` is not an
open-ended parser, it is a *finite, closed set of hardening behaviors* layered on
the standard library's own XML parser — so purexml delivers those same
protections on the stdlib (`xml.etree`, which builds on CPython's `pyexpat`),
directly. The consumer surface is a single hardened call: `fromstring(text) ->
xml.etree.ElementTree.Element`. The anchor consumer is **file-observer**. This is
a *security control*, not a format reader — owning it means owning the audit
burden, which is why the adversarial review leg carries extra weight here. Full
capability spec: [`docs/TARGET_SPECIFICATION.md`](docs/TARGET_SPECIFICATION.md)
(the 1.0 north star); first slice: [`docs/v0.1.0_RFC_Specification.md`](docs/v0.1.0_RFC_Specification.md).

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
  the unified per-project Claude session-jsonl tree (documented exception). If
  that subdir doesn't exist yet, the **First-session bootstrap** chatlog step
  hasn't run — do it.
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

### Agreement on intent is not authorization to execute

When Russell agrees with a *plan* or its *intent*, that is not by itself
permission to start writing files or running state-changing commands —
especially under an explicit read-only / verify-first order. Repeating the plan
back is not the same as being told to do it. Confirm you're in **execute** mode,
not **discuss** mode, before you act. (This is the first item in the
**Decision gates** "before you execute anything" checklist — it's here too
because it's an authorization boundary, and a prior instance broke it moments
after repeating the order back.)

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

> **Gate:** before finalizing an RFC or opening a PR, run the matching
> checklist in **Decision gates** above. A draft is reviewed in conversation,
> never PR'd; the PR is for implementation.

**Version axes for this project** (per [`CONVENTIONS.md`](CONVENTIONS.md) §1):
RELEASE_VERSION is mandatory (`pyproject.toml`). SCHEMA_VERSION is **n/a** —
purexml returns a standard `xml.etree.ElementTree.Element`, not a custom wire
shape, so there is no schema to version. LOGIC_VERSION tracks the **hardening
mitigation set** (which attack classes are blocked, on which path); it bumps if
the same input would parse-or-block differently than before. The matched
`defusedxml` mitigation list (enumerated in the v0.1.0 measure-first task) is the
contract LOGIC must hold.

One-line bullets per version (newest first; copy the shape from
[`HISTORY.md`](HISTORY.md)):

- **v0.1.1** *(shipped 2026-06-16, PR #2)* — **patch**: lower runtime floor to
  Python **3.10** (was 3.12) so purexml never binds a consumer's floor; CI matrix
  tests 3.10–3.13. No logic/behavior change. SCHEMA n/a; LOGIC unchanged (v0.1).
  _HISTORY only, no RFC._
- **v0.1.0** *(shipped 2026-06-16, PR #1)* — first slice: the whole consumer
  contract (C1 safe-parse + C2 safe-failure) via a single hardened `fromstring`,
  behaviorally equivalent to `defusedxml` defaults. Spec:
  [`docs/v0.1.0_RFC_Specification.md`](docs/v0.1.0_RFC_Specification.md);
  compliance: [`docs/COMPLIANCE-v0.1.md`](docs/COMPLIANCE-v0.1.md); four-leg
  review complete. SCHEMA n/a; LOGIC introduced (mitigation set v0.1).

## Stack

See [`STACK.md`](STACK.md) — the canonical record of language, runtime,
dependencies, and any template-variant adaptations.

## Commands

This is a **Python** project (Go half of the template deleted). Install + test:

```bash
pip install -e ".[dev]"
python -m pytest tests/ -q
```

There is no CLI — the surface is the library call `purexml.fromstring(text)`. If
the project grows commands, document them in `STACK.md` or here, not in tribal
knowledge.

## Architecture

Tiny by design (~200 lines of `src/`). The whole public surface is one call.

- **`src/purexml/__init__.py`** — public exports: `fromstring`, the exception
  hierarchy, `ParseError` (re-exported from stdlib), `__version__`.
- **`src/purexml/_parser.py`** — the engine. `fromstring(text)` →
  `_HardenedParser`, built **directly on `xml.parsers.expat` + a
  `xml.etree.ElementTree.TreeBuilder`** (NOT by subclassing `xml.etree`'s
  `XMLParser` — the CPython C accelerator doesn't expose the expat handler hooks;
  see Known decisions). It mirrors the stdlib `XMLParser` expat→tree glue
  (namespace separator `"}"`, `ordered_attributes`, `buffer_text`, `_fixname`
  Clark-notation, undefined-entity handling) so the returned `Element` is
  byte-identical to the stdlib's, then installs the defusedxml-default blocking
  handlers (`EntityDeclHandler`/`UnparsedEntityDeclHandler` → `EntitiesForbidden`;
  `ExternalEntityRefHandler` → `ExternalReferenceForbidden`; no
  `StartDoctypeDeclHandler`, so an entity-free DTD is allowed). `feed_close`
  breaks the parser↔self reference cycle in a `finally`.
- **`src/purexml/errors.py`** — `PureXMLError(ValueError)` ←
  `EntitiesForbidden`, `ExternalReferenceForbidden`. Malformed input raises the
  stdlib `ParseError` unchanged.
- **`tests/`** — the falsify-first battery: `test_equivalence.py` (C14N
  same-parse vs the defusedxml oracle, str+bytes, + the exact consumer surface),
  `test_attacks.py` (attack battery + the no-fetch/no-read proof harness in
  `conftest.py`), `test_misc.py` (malformed parity, version-sync, zero-dep guard,
  the reference-cycle regression). Run on CPython ≥3.10.
- **Out of `src/` (gitignored):** `scratch/review/corpus_sweep.py` — the
  empirical same-parse sweep over file-observer's real corpus (read-only;
  not committed). `scratch/measure/` — the measure-first findings.

## Known decisions

A running list of things future-you (and future agents) will want to know
*before* changing related code. Add a one-line bullet whenever a non-obvious
choice gets locked in — anti-pattern is finding the decision only by `git
blame`.

- **Behavioral equivalence to `defusedxml`, not a fresh design** — the design
  contract is "match what `defusedxml` does on the `fromstring` path," validated
  oracle-gated (target spec §6). We don't invent hardening; we enumerate
  `defusedxml`'s closed mitigation set and match it. This is what makes the
  dependency-removal a clean kill rather than a reimplementation gamble.
- **Stdlib-only, zero runtime deps** — `xml.etree` / `pyexpat`, no third-party
  runtime dependency. `defusedxml` is allowed *only* as a dev/test oracle, never
  shipped (target spec §4). purexml must never become the binding Python floor
  for a consumer.
- **CPython + pyexpat assumption, recorded explicitly** — the hardening assumes
  CPython's stdlib `expat`. Runtimes without pyexpat would need a separate code
  path; see Excluded (IronPython/Jython out of scope). Stay PyPy-portable.
- **Runtime floor = Python 3.10** (set in v0.1.1, 2026-06-16) — lowered from 3.12
  so purexml never binds a consumer's floor (target spec §4; file-observer's real
  floor is ~3.10). **CI-grounded**: the matrix tests 3.10–3.13 on every push, so
  the floor is verified, not asserted. The src uses only long-stable stdlib.
- **Built directly on `xml.parsers.expat` + `TreeBuilder`** (measure-first F5) —
  NOT by subclassing `xml.etree`'s `XMLParser` (CPython's C accelerator hides the
  expat handler hooks), and NOT via defusedxml's fragile pure-Python module
  surgery. The expat→tree glue is a faithful mirror of the stdlib `XMLParser` so
  the `Element` is byte-identical. Don't "modernize" away the mirroring — it is
  the equivalence guarantee.
- **Block exceptions subclass `ValueError`** (measure-first F4) — mirrors
  defusedxml's `DefusedXmlException(ValueError)` MRO so a consumer narrowing to
  `except ValueError` stays equivalent. Malformed input raises the stdlib
  `ParseError` (NOT a `PureXMLError`). Do not reparent these to `ParseError`.
- **Equivalence is proven via `ET.canonicalize` (C14N)** — "same parse" is defined
  as C14N-equal to the defusedxml oracle, not ad-hoc tree comparison. Verified on
  340 real inputs (0 disagreements) + the synthetic battery. Keep the oracle a
  **dev/test-only** dep.
- **External-DTD nuance (measure-first F2)** — an *unresolved* external-DTD
  declaration is **allowed** (parses, no fetch); only *attempted* external
  resolution is blocked. Over-blocking it would break equivalence. Don't "harden"
  by raising on the mere presence of an external DTD.
- **v0.1.0 surface is a single `fromstring`** — the whole consumer contract
  (C1+C2) ships in one slice because value is only realized when "same parses
  succeed" and "same attacks blocked" hold *together* (RFC §1). Small surface,
  load-bearing correctness.
- **1.0 identity = complete drop-in for `defusedxml.ElementTree`** (ratified
  2026-06-16, grounded by `/deep-research` — see `scratch/research/2026-06-16_1.0-scope-research.md`
  and `docs/ROADMAP-to-1.0.md`). Scope = the ElementTree family (`fromstring`,
  `parse`, `iterparse`, `fromstringlist`, `XMLParser`, `XML`/`tostring`,
  `ParseError`); minidom/sax/pulldom/xmlrpc/lxml **deferred, not excluded**.
  purexml's value beyond a 1:1 mirror: it *tracks current CPython/libexpat
  mitigations* defusedxml (frozen 2021, abandoned) never got.
- **`forbid_*` knobs are IN scope** (re-opened 2026-06-16; was Excluded for
  v0.1.0). A true drop-in must accept defusedxml's parameterized signature
  (`forbid_dtd`/`forbid_entities`/`forbid_external`, identical defaults). They
  land in v0.2. (See the tombstone in Excluded decisions.)
- **Posture = behavioral mirror + bounded, opt-in defense-in-depth** — mirror
  defusedxml's *defaults* for compatibility, but add what defusedxml lacks:
  runtime `pyexpat.EXPAT_VERSION` assertion, reparse-deferral awareness
  (CVE-2023-52425), amplification-limit awareness, optional `forbid_dtd=True`
  strict mode (OWASP). At 1.0 freeze the mirror surface STABLE, keep the novel
  defense-in-depth PROVISIONAL (moving libexpat landscape).
- **Adoption model DEFERRED TO v1.0** (decided 2026-06-16) — file-observer may
  *vendor* purexml (its leaning) or take it as a *first-party dependency*; the
  choice is **deliberately not made until v1.0.** Everything that rides on it is
  therefore also deferred: PyPI publishing, claiming the `purexml` name (confirmed
  free 2026-06-15), the license, and the **vendor single-file form** (scanner #6).
  Until 1.0, purexml ships as the `src/purexml/` package in the private repo only,
  consumed via git/path or by vendoring the package as-is. Do **not** publish,
  claim the name, set a license, or build the single-file amalgamation before the
  1.0 adoption decision. See `scratch/packaging_and_naming_notes.md`.

## Excluded decisions (do NOT re-introduce)

The counterpart to `Known decisions`: things Russell has **explicitly ruled
out.** Record each one here the moment it's excluded, so a later session (or a
reset instance) can check against it before proposing — re-introducing an
excluded element is a documented failure mode of this template. Pattern:
"**X** — excluded <date>, because Y. Do not bring back without re-opening with
Russell."

> Note: these originate as **scope boundaries set by the target spec / RFC**
> (authored by the file-observer instance), not yet as in-conversation Russell
> rulings. They function identically — re-introducing one is the documented
> failure mode — so they are recorded here. Re-opening any of them is a
> conscious decision to make *with* Russell, not a quiet expansion of scope.

- **IronPython / Jython support** — out of scope (target spec §4). No .NET/JVM
  consumer exists; their non-pyexpat XML parsers would need a separate hardening
  path. Do not add without a real consumer + re-opening with Russell.
- **XML writing / serialization** — out of scope (RFC §5). purexml is parse-only;
  it is a hardened *reader*, never a writer.
- **Parse modes beyond `fromstring`** (`iterparse`, SAX, `parse`-from-file) —
  out of scope for v0.1.0 (RFC §6). file-observer needs only `fromstring`. Add
  later *only* if a consumer actually needs them, as its own slice.
- **Configurable hardening flags** (`forbid_dtd` / `forbid_entities` /
  `forbid_external` knobs) — ~~out of scope for v0.1.0~~ **RE-OPENED 2026-06-16
  for the 1.0 general-replacement scope** (ratified by Russell). Originally
  excluded when the only consumer was file-observer (one fixed behavior; a tunable
  control is a misconfiguration surface). The 1.0 scope changed to "complete
  drop-in for `defusedxml.ElementTree`," which *requires* matching defusedxml's
  parameterized signature. The knobs are now **in scope** — see Known decisions.
  Tombstone kept so the reversal is a recorded decision, not a silent regression.
- **Publishing to PyPI / claiming the `purexml` name** — explicitly held until
  the adoption model (vendor vs first-party dep) is decided. Free-name status is
  recorded, not acted on. (Cross-reference: Known decisions, last bullet.)

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

> **Gate:** "run all four on minors+" is a requirement, not a suggestion.
> Running fewer is a decision you make and *record* (in the PR / findings log),
> not a default you slide into. Before opening a PR, run the **Decision gates**
> "before opening a PR" checklist. A prior instance ran this as one-and-a-half
> legs without noticing — the silent-regression failure this whole contract guards.

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
