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
  cross-model, repo-clone/empirical sweep — **at the depth the Review-tier rubric
  sets for this change type**? (The fourth leg, PR bots, fires *on PR open* — it's
  checked at the before-merge gate, not here.) Scaling down is a decision you make
  and *record in the PR/findings* (per the rubric), not a default you slide into.
- [ ] Are those findings logged in `scratch/review/`?
- [ ] Is this implementation (PR-worthy), not a draft (conversation)?
- [ ] Did I re-introduce anything in `Excluded decisions`?
- [ ] **libexpat currency:** ran `python tools/check_expat_currency.py` (IN-SYNC, or
  drift surfaced)? See the libexpat Known decision.

**Before merge (minors):**
- [ ] Did the PR-bot leg fire (**CodeRabbit** — the async leg-4 bot, auto on PR open), and are
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
directly. As of **v0.3 the consumer surface is the full `defusedxml.ElementTree`
family** — `fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`,
`XMLParser`, `tostring`, the `forbid_*` knobs — under a canonical
`purexml.ElementTree` namespace, so migration is a literal `s/defusedxml/purexml/`.
**The surface has broadened well beyond ElementTree** — `purexml.minidom` (v0.10, the #2
consumer surface) + `purexml.sax` (v0.12, #3) ship, with `purexml.common` for catch-site compat.
The anchor consumer is **file-observer** (it uses only `fromstring`), but the **1.0 identity
reframed 2026-06-19**: not the ElementTree slice one adopter needs, but *the maintained, zero-dep
successor that replaces defusedxml across the surface the ecosystem actually imports*
(measured: ElementTree ✅, minidom ✅, **sax ✅**, expatreader ✅, **xmlrpc ✅ (v0.13)**, common ✅;
pulldom deferred, lxml excluded on zero-dep identity — see Known/Excluded decisions +
`docs/ROADMAP-to-1.0.md`). **The measured breadth surface is COMPLETE, and the 1.0 contract is FROZEN + binding (v1.0.0, 2026-07-08 — `PUBLIC_CONTRACT.md` + `docs/v1.0.0_RFC_Specification.md`, ratified with file-observer).** What remains is Russell's separate PyPI-publish + name-claim call. This is a
*security control*, not a format reader — owning it means owning the audit burden,
which is why the adversarial review leg carries extra weight here. Capability
north star: [`docs/FO_REQUIRED_COMPATIBILITY.md`](docs/FO_REQUIRED_COMPATIBILITY.md); the
plan to 1.0: [`docs/ROADMAP-to-1.0.md`](docs/ROADMAP-to-1.0.md).

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
| `agy` (Antigravity CLI) | The Gemini surface for the cross-model review leg, on the **paid AI Pro** subscription (replaced the free-key `gemini` CLI 2026-06-29). Model-selectable (`agy models`); `agy plugin import gemini` adds the maestro/code-review extensions. | Blueprint `gemini-review-infra` doc |
| review-kit legs at `/srv/projects/review-kit/` | `route.sh` (orchestrator — picks legs by heat/health), `gpt.sh` (OpenAI — the genuinely **independent** cross-family vote vs a Claude author), `gem-pro.sh` (Gemini inline, on `agy`), `gem-review.sh` (agy+maestro whole-codebase red-team, `/tmp`-snapshot-guarded), `static.sh` (non-LLM shellcheck/semgrep), `deps.sh` (osv-scanner CVE). Consume by copy, **change by issue** on `russalo/review-kit`. | `/srv/projects/review-kit/README.md` |
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

- **v1.0.0** *(shipped 2026-07-08)* — **THE CONTRACT FREEZE.** The `defusedxml`-mirror surface
  (module namespaces, function signatures + defaults, the complete exception hierarchy, the
  `>=3.10` floor, `__version__`) is now **STABLE to 2.0** (`PUBLIC_CONTRACT.md` filled + binding;
  guarded by `tests/test_public_contract.py`). The opt-in defense-in-depth (`Limits`,
  `security_report()`, the version-assertion surface) stays **PROVISIONAL** by design — freezing
  it would block hardening against new expat CVE classes without a 2.0. **Ratified by Russell +
  the file-observer steward (2026-07-07)** (FO pins `purexml.ElementTree.fromstring`, adopts
  post-1.0; FO's 6-point contract all inside the frozen surface incl. its floor + `__version__`
  gap-check). **No parse-or-block change** — a governance/contract freeze, not a feature release;
  LOGIC unchanged, SCHEMA n/a; Development Status → Production/Stable. PyPI publish + name-claim
  remain a separate strategic step (repo-side freeze is done; the package is not yet published).
  [RFC](docs/v1.0.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v1.0.md).
- **v0.14.1** *(shipped 2026-06-28)* — **patch: license = MIT**. Adds `LICENSE` (MIT, © 2026
  Russell Pfister), `license = {text = "MIT"}` + the OSI MIT classifier in `pyproject.toml`
  (table form, not the bare SPDX string — keeps the classifier without the PEP 639 warning on
  the setuptools≥65 floor), and swaps the "license deferred" placeholders in README/STACK for
  MIT. Rationale (Russell): give-it-away zero-dep infrastructure → pure OSS, max reuse, no
  commercial-upside concern (deliberate opposite of file-observer's AGPL-3.0 + dual-commercial);
  MIT is one-way AGPL-compatible, so purexml stays clean as a future FO dependency. **Sets the
  pure\* family default** (purecfb/puresniff) unless a lib flags a reason to differ. Publish +
  name-claim stay deferred (license settled; publish trigger separate). No code/parse change;
  LOGIC unchanged, SCHEMA n/a. _HISTORY only._
- **v0.14.0** *(shipped 2026-06-27, PR #37)* — **extend opt-in `Limits` to minidom + sax**: the v0.4
  structural-DoS caps (`max_depth`/`max_attributes`/`max_bytes`) now reach the breadth surfaces via a
  keyword-only `*, limits=None` — opt-in, default-off (with `limits=None` minidom/sax stay
  byte-identical; differential fuzz + sweep 372/0 confirm). A shared `_LimitCounter` in `limits.py`
  keeps accounting identical to the ElementTree path (same `DepthExceeded`/`AttributesExceeded`/
  `SizeExceeded`). `max_bytes` enforced on `parseString` only (stream length unknown without `os`);
  depth/attrs also on `parse(file/stream)`. **xmlrpc deferred** (no `limits=` call site; gzip-bomb
  `MAX_DATA` is its cap). Closes the last of three post-breadth gaps (A=fuzz-all-surfaces v0.13.1,
  B=multi-surface re-soak #36, C=Limits breadth). New caps on new surfaces → **LOGIC extended**;
  SCHEMA n/a. Full four-leg (security-load-bearing); 1 PR-bot finding (Gemini init-ordering on
  expatreader) grounded as not-a-live-bug + applied anyway as parity/robustness; limits/minidom/sax/
  expatreader 100% cov. [RFC](docs/v0.14.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v0.14.md).
- **v0.13.0** *(shipped 2026-06-26, PR #34)* — **`purexml.xmlrpc` (lazy-monkeypatch shim)**: the
  last non-negligible measured module (343 sites) and a *different shape* — a monkeypatch of the
  stdlib `xmlrpc`, not a parse fn. `monkey_patch()`/`unmonkey_patch()` install/restore a defused
  expat parser (`FastParser`) + a **bounded gzip** decode (`MAX_DATA`=30 MB, anti-decompression-bomb
  — purexml's first non-XML defense) on `xmlrpc.client`/`server`. **Option C (Russell's call):** all
  `xmlrpc`/`gzip` imports are LAZY (inside `monkey_patch()` + gzip helpers), so `import purexml`
  never pulls the network-capable transport — proven in a subprocess; `socket`/`http` stay FORBIDDEN
  even here (a static `XMLRPC_EXTRA` carve-out covers only the lazy `xmlrpc`/`gzip`). New surface →
  LOGIC extended; SCHEMA n/a; zero-dep + no-I/O-at-import intact. Full four-leg; 4 PR-bot findings
  (incl. a gzip-bomb `read(-1)` memory hole) all real + fixed. **This completes the measured breadth
  surface — next is the 1.0 freeze.** [RFC](docs/v0.13.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v0.13.md).
- **v0.12.0** *(shipped 2026-06-26, PR #31)* — **`purexml.sax` + `purexml.expatreader` drop-in**:
  the next breadth module (sax = 375 sites; expatreader promoted *deferred→done* as its engine).
  Event-driven — `make_parser`/`parse`/`parseString` drive a caller's `ContentHandler`; hardening
  installed in `reset()` on the stdlib `xml.sax.expatreader.ExpatParser`, raising purexml's
  exceptions (arg-mapped as in `_parser.py`/`minidom.py`). `parseString` is **bytes-only** (mirrors
  defusedxml exactly; `str`→`TypeError` on both — no over-accept, the minidom/pathlib lesson).
  Malformed → stdlib `SAXParseException` (not a `PureXMLError`). New parse surface → LOGIC extended;
  SCHEMA n/a; zero-dep intact. Full four-leg; event-stream parity vs oracle; sax+expatreader 100% cov.
  *(RFC §3.4 refined: the SAX reader is no-leak/gc-collected — a residual pyexpat exception-retention
  cycle, parity with defusedxml.sax — NOT fully refcount-reclaimable like ElementTree/minidom.)*
  [RFC](docs/v0.12.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v0.12.md).
- **v0.11.0** *(shipped 2026-06-26, PR #30)* — **map the reachable libexpat 2.8.2 batch**: the
  follow-up to v0.10.1's floor patch (v0.5.1→v0.6 lifecycle). Grounded that **7 of the 2.8.2 CVEs
  reach purexml's ordinary parse paths** (storeAtts/addBinding/getAttributeId/XML_ParseBuffer/
  textLen/copyString/doProlog); the reentrant-handler/suspend-resume trio (50219/56131/56412) +
  xmlwf trio (56409–56411) do **not**. Adds one **aggregate** class
  `integer_overflow_dos_expat_2_8_2` (EXPAT_MITIGATED ≥2.8.2 else LIVE; the 7 share fix version +
  status + nature) and **retires the v0.10.1 interim `_HIGHEST_UNMAPPED_FIX`** (every reachable fix
  tracked again). Report-only; no parse-behavior change; SCHEMA n/a; LOGIC unchanged.
  [RFC](docs/v0.11.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v0.11.md).
- **v0.10.1** *(shipped 2026-06-26)* — **patch: libexpat-floor currency**. The release-time
  currency gate caught **libexpat 2.8.2** (2026-06-25) — a large integer-overflow/memory-
  corruption release with classes reachable via ordinary attribute/namespace/text/DOCTYPE
  parsing. Bumps `RECOMMENDED_EXPAT_VERSION` 2.8.1 → 2.8.2 (report data) and **re-arms the
  generic floor advisory** (`_HIGHEST_UNMAPPED_FIX = 2.8.2`) so a runtime below 2.8.2 is told it
  may be missing the not-yet-individually-mapped 2.8.2 batch. Per-class mapping is the v0.11.0
  minor (the v0.5.1→v0.6 lifecycle). No parse-behavior change; SCHEMA n/a; LOGIC unchanged.
  _HISTORY only, no RFC._
- **v0.10.0** *(shipped 2026-06-19, PR #28)* — **`purexml.minidom` drop-in + `purexml.common`
  shim**: first breadth beyond ElementTree, scoped by measured defusedxml usage (minidom = 457
  sites, #2 surface). `parse`/`parseString` → stdlib `xml.dom.minidom.Document`, defusedxml's
  `forbid_*` signature + defaults; hardening mirrors defusedxml (subclass `xml.dom.expatbuilder`,
  install blocking handlers raising purexml's exceptions). Custom `parser=` → `NotSupportedError`
  (stricter than defusedxml). `purexml.common` aliases `DefusedXmlException = PureXMLError` for
  catch-site migration. New parse surface → LOGIC extended; SCHEMA n/a; zero-dep intact.
  Full four-leg (security-load-bearing; legs 1–3 clean, Gemini APPROVED); minidom+common 100% cov.
  [RFC](docs/v0.10.0_RFC_Specification.md) · [compliance](docs/COMPLIANCE-v0.10.md).
- **v0.9.0** *(shipped 2026-06-19, PR #27)* — **map CVE-2026-41080 (hash-flooding)**:
  closes the class v0.6 deferred "until grounded". Grounded as insufficient SipHash salt
  entropy (CWE-331, expat 2.8.0, LOW) reachable via normal name-interning; added to
  `security_report().mitigations` as `hash_flooding_cve_2026_41080`. Because it's a
  *hardening* of an existing defense (not a present/absent hole), introduces a 5th status
  **`EXPAT_PARTIAL`** — **never `LIVE`**, and (refined per PR#27 Codex, CVE-2026-7210)
  reported **conservatively PARTIAL on every runtime**: full 16-byte-salt mitigation needs
  BOTH expat ≥2.8.0 AND CPython's `pyexpat` fix (which purexml can't verify at runtime), so
  it never claims `MITIGATED` on the expat version alone. Also **retires
  `_HIGHEST_UNMAPPED_FIX`** + the generic untracked-gap advisory — every *reachable* expat
  fix is now individually tracked. Report-only; no parse-behavior change; SCHEMA n/a; LOGIC
  unchanged (reported, not blocked); status vocabulary PROVISIONAL. Four-leg review (legs
  1–3 clean; report-only tier). [RFC](docs/v0.9.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.9.md).
- **v0.8.0** *(shipped 2026-06-18, PR #21)* — **ship types**: annotate the
  public surface + a PEP 561 `py.typed` marker (consumers' type-checkers use purexml's
  types, not `Any`); `mypy`-clean gated by a CI typecheck job; `types: mypy` badge. The
  verbatim-mirror `_setevents` redefinitions + the structural-stdlib-drop-in friction kept
  via documented `# type: ignore`s (mirror preserved). Added `typing`/`__future__` to the
  no-I/O allowlist (pure, lazy annotations). No runtime/parse change; SCHEMA n/a; LOGIC
  unchanged. [RFC](docs/v0.8.0_RFC_Specification.md).
- **v0.8.1** *(2026-06-18)* — **patch**: tighten mypy to `--strict` (no behavior/API
  change). Annotated all internal `_parser.py` methods; `Any` leaks resolved (`cast` on
  the pluggable-target `close()`); the verbatim `_setevents` mirror kept byte-for-byte via
  `# type: ignore[misc, no-untyped-def]`; expat handle + target typed `Any`. CI `mypy`
  now runs strict. _HISTORY only._
- **v0.7.0** *(shipped 2026-06-17, PR #15)* — **posture CLI**:
  `python -m purexml` over `security_report()` — default human report (informs, exit 0),
  `--json` (machine-readable, PROVISIONAL), `--check [--min-expat X.Y.Z]` (opt-in CI gate,
  pin-your-floor), `--version`; + `SecurityReport.as_dict()`. First build of the
  publish-worthy-debut push. `__main__.py` is the one I/O boundary (no-I/O guard
  carve-out: may add argparse/json/sys, still under FORBIDDEN). No parse-behavior change;
  SCHEMA n/a; LOGIC unchanged. [RFC](docs/v0.7.0_RFC_Specification.md).
- **v0.6.0** *(shipped 2026-06-17, PR #11)* — **complete the posture map**: adds the two
  newer expat-layer DoS classes (`content_token_overflow_cve_2026_25210` → expat 2.7.4;
  `attribute_collision_dos_cve_2026_45186` → 2.8.1, opt-in `max_attributes` partially
  bounds it) as first-class `security_report().mitigations` entries with per-class
  fix-version gating. Report-only; no parse-behavior change. CVE-2026-41080 left unmapped
  (ungrounded; cited in the floor advisory only below 2.8.0). Four-leg review; 1 PR-bot
  finding (2.8.0 advisory precision) grounded + fixed. SCHEMA n/a; LOGIC unchanged
  (reported, not blocked). [RFC](docs/v0.6.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.6.md).
- **v0.5.1** *(2026-06-17)* — **patch**: adversarial soak + expat-floor currency (no
  parse-behavior change). 17-vector red-team soak module (incl. encoding-vector attacks
  proving encoding-independent blocking) + 60k-comparison heavy differential soak (0
  divergences). **`RECOMMENDED_EXPAT_VERSION` 2.7.2 → 2.8.1** (2026 libexpat 2.7.4–2.8.1
  DoS train; CVE-2026-25210/41080/45186 reach normal parse paths), `disproportionate_memory`
  decoupled onto its own 2.7.2 fix version. Adding the new reachable DoS classes to the
  mitigation map is deferred (mitigation-set change). LOGIC unchanged. _HISTORY only._
- **v0.5.0** *(shipped 2026-06-17, PR #8)* — **trust surface**: read-only
  `security_report()` posture API (libexpat version + per-class mitigation map +
  `RECOMMENDED_LIMITS`; genuinely immutable via `MappingProxyType` + `__new__`/`_make`
  normalization) + audit evidence (960-doc differential fuzz, opt-in Atheris `[fuzz]`
  extra, committed `docs/EQUIVALENCE.md`). First minor under the maintained-successor
  mandate; no parse-behavior change. Four-leg review; 5 PR-bot findings all real +
  fixed. SCHEMA n/a; LOGIC unchanged. [RFC](docs/v0.5.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.5.md).
- **v0.4.0** *(shipped 2026-06-16, PR #7)* — opt-in structural-DoS caps
  (`max_depth`/`max_attributes`/`max_bytes`, default-OFF) raising `LimitExceeded` — the
  first deliberate divergence beyond defusedxml (opt-in only; default path stays
  byte-equivalent). Four-leg review; all 4 PR-bot findings real + fixed. SCHEMA n/a;
  LOGIC extended (structural caps). [RFC](docs/v0.4.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.4.md).
- **v0.3.1** *(shipped 2026-06-16, PR #6)* — **patch**: Tier-1 hardening
  (within-mirror) — a structural no-I/O import guard (`src` imports only stdlib
  `xml`; no network/exec/os) + broadened differential fuzz. No behavior change.
  _HISTORY only._
- **v0.3.0** *(shipped 2026-06-16, PR #5)* — hardened `iterparse`; **completes the
  `defusedxml.ElementTree` family** (the streaming slice; Option A — `_setevents`
  + reuse stdlib iterparse). Four-leg review; all 3 PR-bot findings grounded-declined.
  SCHEMA n/a; LOGIC unchanged. [RFC](docs/v0.3.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.3.md).
- **v0.2.0** *(shipped 2026-06-16, PR #4)* — non-streaming ElementTree surface
  (`parse`/`fromstringlist`/`XML`/`tostring`/`XMLParser`) + the `forbid_*` knobs
  (+ `DTDForbidden`) under the `purexml.ElementTree` namespace. SCHEMA n/a; LOGIC
  mitigation set extended (`forbid_dtd`). [RFC](docs/v0.2.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.2.md).
- **v0.1.2** *(shipped 2026-06-16, PR #3)* — **patch**: durability hardening — the
  differential fuzz gate vs the oracle, the 2 newer expat-layer attack classes
  (CVE-2023-52425 + disproportionate-memory, version-gated), and the opt-in
  libexpat version-awareness API. No behavior change. _HISTORY only._
- **v0.1.1** *(shipped 2026-06-16, PR #2)* — **patch**: lower runtime floor to
  Python **3.10**; CI matrix 3.10–3.13. No behavior change. _HISTORY only._
- **v0.1.0** *(shipped 2026-06-16, PR #1)* — first slice: hardened `fromstring`
  (C1 safe-parse + C2 safe-failure), behaviorally equivalent to `defusedxml`
  defaults. [RFC](docs/v0.1.0_RFC_Specification.md) ·
  [compliance](docs/COMPLIANCE-v0.1.md). SCHEMA n/a; LOGIC introduced (set v0.1).

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

Small by design (~300 lines of `src/`). The whole engine is one class.

- **`src/purexml/_parser.py`** — the engine. The public **`XMLParser`** is built
  **directly on `xml.parsers.expat` + a `xml.etree.ElementTree.TreeBuilder`** (NOT
  by subclassing `xml.etree`'s `XMLParser` — the CPython C accelerator doesn't
  expose the expat handler hooks; see Known decisions). It mirrors the stdlib
  `XMLParser` expat→tree glue (separator `"}"`, `ordered_attributes`,
  `buffer_text`, `_fixname` Clark-notation, undefined-entity handling) so the
  `Element` is byte-identical, then installs the blocking handlers per the
  `forbid_*` flags (`EntityDeclHandler`/`UnparsedEntityDeclHandler` →
  `EntitiesForbidden`; `ExternalEntityRefHandler` → `ExternalReferenceForbidden`;
  `StartDoctypeDeclHandler` → `DTDForbidden` only when `forbid_dtd=True`). It also
  implements **`_setevents`** (a verbatim stdlib mirror) so it drives stdlib
  `iterparse`. `feed`/`close` clean up the parser↔self cycle on **every** path
  (success or error). Functions: `fromstring`, `parse` (via stdlib `parse`),
  `fromstringlist`, `iterparse` (via stdlib `iterparse`). Each takes the keyword-only
  `limits=` (v0.4); depth/attr accounting is in `_start`/`_end` (decoupled from the
  target callbacks) and `max_bytes` counts UTF-8 bytes in `feed`.
- **`src/purexml/ElementTree.py`** — the canonical `purexml.ElementTree` namespace
  mirroring `defusedxml.ElementTree` (the `s/defusedxml/purexml/` surface):
  re-exports the family + `XML`/`XMLParse`/`XMLTreeBuilder` aliases + stdlib
  `ParseError`/`tostring`.
- **`src/purexml/minidom.py`** — `purexml.minidom`, the hardened drop-in for
  `defusedxml.minidom` (v0.10). `parse`/`parseString` → stdlib `xml.dom.minidom.Document`.
  Hardening mirrors defusedxml: a `_DefusedExpatBuilder` / `_DefusedExpatBuilderNS` subclass of
  stdlib `xml.dom.expatbuilder.ExpatBuilder`/`Namespaces` whose `install()` adds the SAME
  blocking handlers as `_parser.py` (arg-mapped to purexml's exception signatures). A
  caller-supplied `parser=` raises `NotSupportedError` (a foreign parser would bypass hardening —
  stricter than defusedxml's parser-patching); `bufsize=` accepted for compat, result identical.
  Keyword-only `limits=` (v0.14): depth/attr accounting overrides the element handlers on
  `_DefusedExpatBuilderNS` (Namespaces owns them in the MRO; `_counter` set BEFORE `super().__init__`
  since `ExpatBuilder.__init__` calls `reset()`); attrs are an ordered list → count = `len//2`.
  `max_bytes` on `parseString` only.
- **`src/purexml/common.py`** — `purexml.common`, the exception-compat shim (v0.10): re-exports
  the block exceptions + `NotSupportedError` and aliases `DefusedXmlException = PureXMLError`, so
  `except DefusedXmlException` survives `s/defusedxml/purexml/` across every module. Compat layer
  only — the top-level `purexml` namespace stays purexml-native.
- **`src/purexml/expatreader.py`** — `purexml.expatreader` (v0.12), the hardened SAX driver:
  `_DefusedExpatParser(xml.sax.expatreader.ExpatParser)` installs the same blocking handlers as
  `_parser.py`/`minidom.py` **in `reset()`** (where the stdlib reader (re)creates `self._parser`);
  `create_parser()` returns it. `parse()` clears the reader→parser edge on every path (minidom
  PR#28 hygiene) — but the SAX reader is only *gc-collected*, not refcount-reclaimable (residual
  pyexpat exception-retention cycle; defusedxml.sax has it too). Keyword-only `limits=` (v0.14):
  overrides `start_element`/`end_element` + the NS-on `start_element_ns(name, attrs)`/`end_element_ns(name)`
  (grounded signatures); attrs are a dict → count = `len`. `_counter` set before `super().__init__`
  for parity (grounded: `ExpatParser.__init__` doesn't call reset(), so latent-robustness not a live fix).
- **`src/purexml/sax.py`** — `purexml.sax` (v0.12), the `defusedxml.sax` drop-in: `make_parser`
  (`parser_list` accepted+ignored — always its own hardened reader), `parse`, `parseString`
  (**bytes-only**, mirroring defusedxml's `BytesIO(string)`). Malformed → stdlib `SAXParseException`.
  Keyword-only `limits=` (v0.14) threads through `make_parser` → `create_parser`; `parseString`
  also checks `max_bytes`.
- **`src/purexml/xmlrpc.py`** — `purexml.xmlrpc` (v0.13), the `defusedxml.xmlrpc` drop-in. NOT a
  parse fn — a **lazy monkeypatch shim** (option C): `monkey_patch()`/`unmonkey_patch()` swap a
  defused `xmlrpc.client.ExpatParser` subclass (`FastParser`) + bounded gzip (`MAX_DATA`,
  anti-bomb) onto `xmlrpc.client`/`server`, restoring captured originals on undo. **All
  `xmlrpc`/`gzip`/`io` imports are LAZY** (inside the functions / lazy class factories — a
  module-level class would import the transport at import time), so `import purexml` stays
  network-free until a consumer calls `monkey_patch()`. `setattr` for the stdlib patch
  assignments (mypy-clean). The no-I/O guard carves out only `xmlrpc`/`gzip` for this file;
  `socket`/`http` stay forbidden (purexml never imports the transport).
- **`src/purexml/__init__.py`** — top-level convenience re-exports of the family +
  exceptions + the expat-version API + `__version__`; imports the `ElementTree` submodule.
- **`src/purexml/__main__.py`** — the `python -m purexml` posture CLI (v0.7): prints
  `security_report()` (default), `--json`, `--check [--min-expat]` (opt-in gate),
  `--version`. The package's one I/O boundary; reads `_es.EXPAT_VERSION` at call time so
  it stays consistent with `security_report()` (and testable under monkeypatch).
- **`src/purexml/errors.py`** — `PureXMLError(ValueError)` ← `DTDForbidden`,
  `EntitiesForbidden`, `ExternalReferenceForbidden`, `LimitExceeded`(←`Depth`/
  `Attributes`/`SizeExceeded`). Malformed → stdlib `ParseError`.
- **`src/purexml/limits.py`** — opt-in structural-DoS caps (v0.4): `Limits`
  (`max_depth`/`max_attributes`/`max_bytes`, default `None`) + `RECOMMENDED_LIMITS`. v0.14
  adds the shared `_LimitCounter` (enter/leave/reset depth+attr accounting), `_counter_for(limits)`
  (None when no depth/attr cap), and `_check_max_bytes(data, limits)` — reused by minidom + sax so
  the breadth surfaces enforce caps identically to the ElementTree path.
- **`src/purexml/_expat_security.py`** — opt-in libexpat version-awareness
  (`EXPAT_VERSION`, `expat_is_secure`/`assert_expat_secure`; default floor =
  `RECOMMENDED_EXPAT_VERSION`, **latest-stable**, bumped as libexpat ships fixes) **+
  the `security_report()` posture API** (v0.5): a read-only, immutable `SecurityReport`
  whose `mitigations` map gates each attack class on its OWN expat fix version
  (`_DISPROPORTIONATE_MEMORY_FIXED`/`_CONTENT_TOKEN_OVERFLOW_FIXED`/`_HASH_FLOODING_FIXED`/`_ATTRIBUTE_COLLISION_FIXED`/`_INTEGER_OVERFLOW_BATCH_FIXED`),
  decoupled from the moving recommended-latest floor. Status vocabulary is `BLOCKED`/
  `EXPAT_MITIGATED`/`EXPAT_PARTIAL`/`OPT_IN`/`LIVE` — `EXPAT_PARTIAL` (v0.9) is for a
  *hardening-not-hole* class (CVE-2026-41080: defense present, the fix strengthens it), so it
  is **never `LIVE`**. The 2.8.2 integer-overflow batch is mapped as ONE aggregate class
  `integer_overflow_dos_expat_2_8_2` (v0.11; 7 CVEs sharing the 2.8.2 fix version). As of v0.11
  every *reachable* expat fix is individually mapped again, so there is no generic untracked-gap
  advisory (the v0.10.1 interim `_HIGHEST_UNMAPPED_FIX` retired).
- **`tests/`** — the falsify-first battery: `test_equivalence` / `test_v02_surface`
  / `test_v03_iterparse` (C14N same-parse + event-stream + knob-matrix equivalence
  vs the oracle), `test_attacks` + `test_fuzz_equivalence` + `test_hardening_soak` +
  `conftest` (attack battery + differential fuzz + red-team soak + the no-fetch/no-read
  trip-wire), `test_v04_limits`, `test_v05_security_report` (posture API + version-gating),
  `test_v07_cli` (the `python -m purexml` flag matrix + JSON + --check exit codes),
  `test_no_io` (structural import guard, incl. the `__main__.py` CLI carve-out),
  `test_fo_contract` (the file-observer six-point consumer contract as a named CI gate —
  bytes/str parity, default-safe + opt-in-typed hostile input, a bounded-*time* never-hang
  tripwire, the `.common` exception mirror, determinism, flat surface + `>=3.10` floor,
  `__version__`-is-`str`; a break fails CI as a labeled FO regression),
  `test_durability` / `test_expat_security` / `test_misc`. Run on CPython ≥3.10.
- **Out of `src/` (gitignored `scratch/`):** `review/corpus_sweep.py` (empirical
  sweep over the shared pkplab corpus via symlinks — baseline pinned in committed
  `corpus_manifest.json`); `measure/` (measure-first findings); `spinoff_ideas.md`.

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
- **Leg-3 corpus = the shared pkplab root, via symlinks** (`/srv/projects/pkplab/
  scanner-corpora/`, scanner-owned shared asset for the `pure*` labs). purexml's
  subset (`corpora/tika` + the OOXML fixtures) is **symlinked** into gitignored
  `scratch/corpora/`; `scratch/review/corpus_sweep.py` reads those symlinks. **Never
  commit corpus bytes** (leak + determinism). Instead, the committed
  `corpus_manifest.json` pins counts + per-file sha256 + an aggregate hash of the
  exact subset the sweep gates on — that's the reproducibility anchor. Recipe +
  capability map: the shared root's `README.md`.
- **External-DTD nuance (measure-first F2)** — an *unresolved* external-DTD
  declaration is **allowed** (parses, no fetch); only *attempted* external
  resolution is blocked. Over-blocking it would break equivalence. Don't "harden"
  by raising on the mere presence of an external DTD.
- **v0.1.0 surface is a single `fromstring`** — the whole consumer contract
  (C1+C2) ships in one slice because value is only realized when "same parses
  succeed" and "same attacks blocked" hold *together* (RFC §1). Small surface,
  load-bearing correctness.
- **1.0 identity — REFRAMED 2026-06-19: the maintained zero-dep successor across the surface
  the ecosystem actually imports, NOT the ElementTree slice one adopter needs** (ratified by
  Russell, grounded by the usage measurement `scratch/research/2026-06-19_defusedxml-usage-measurement.md`).
  Supersedes the 2026-06-16 "complete drop-in for `defusedxml.ElementTree`" call (kept as a
  tombstone: ElementTree was the right *first* axis, not the whole 1.0). The forcing function:
  ElementTree-only gives a stranger no reason to adopt unless they use exactly that slice —
  "you'll never get more if you stop there." **Earned 1.0 scope:** ElementTree ✅ (v0.1–v0.3),
  **minidom ✅ (v0.10, 457 sites)**, **sax (375 sites) — next breadth minor**, xmlrpc (343,
  distinct monkeypatch shape) TBD as its own slice; pulldom/expatreader **deferred**
  (measured-negligible); **lxml excluded** on zero-dep identity (Excluded ledger). Two axes make
  the 1.0: **breadth** (cover what the ecosystem imports → a stranger *can* adopt) + **depth**
  (the maintained libexpat/pyexpat tracking + posture report → *why* purexml beats staying on
  abandoned defusedxml). Don't regress to "ElementTree is enough."
- **`forbid_*` knobs are IN scope** (re-opened 2026-06-16; was Excluded for
  v0.1.0). A true drop-in must accept defusedxml's parameterized signature
  (`forbid_dtd`/`forbid_entities`/`forbid_external`, identical defaults). They
  land in v0.2. (See the tombstone in Excluded decisions.)
- **Identity = "strict defusedxml mirror by DEFAULT, plus OPT-IN defense-in-depth"**
  (mirror-plus, **ratified 2026-06-16** at v0.4). Mirror defusedxml's *defaults* for
  drop-in compatibility (the default path stays byte-equivalent), but add what
  defusedxml lacks, **opt-in**: runtime `pyexpat.EXPAT_VERSION` assertion (v0.1.2),
  the `forbid_dtd=True` OWASP strict mode (v0.2), and **opt-in structural-DoS caps**
  (`max_depth`/`max_attributes`/`max_bytes`, v0.4 — defusedxml + the expat cap don't
  bound structural DoS; **extended to minidom + sax in v0.14** via a shared `_LimitCounter`,
  same caps/exceptions, default-off so the breadth mirror stays byte-identical). **Rule: any defense-in-depth is OPT-IN, default-OFF — never
  diverge from defusedxml by default.** At 1.0 freeze the mirror surface is STABLE;
  the novel defense-in-depth is PROVISIONAL (it may evolve). See `docs/v0.4.0_RFC_Specification.md`.
- **Adoption model: DIRECTION decided = publish first-party; LICENSE decided = MIT;
  PUBLISH SPECIFICS deferred** (direction ratified 2026-06-16; license ratified
  2026-06-28). purexml is an **ecosystem-adoptable, first-party library** (not vendor-only)
  — that's the mandate (`docs/v1.0_TARGET.md`). **License is now SET: MIT** (applied
  v0.14.1; `LICENSE` + pyproject; rationale below). The *remaining* specifics — PyPI
  publish timing, claiming the `purexml` name (confirmed free 2026-06-15, re-confirmed
  2026-06-27), the optional vendorable single-file form — stay deferred to a deliberate
  strategic call. **Until then: do NOT publish or claim the name** — repo-only, consumed via
  git/path. (The "do NOT set a license" half of this is now SUPERSEDED — license is MIT.)
  - **License = MIT** (Russell, 2026-06-28): give-it-away, zero-dep infrastructure → pure
    OSS, maximum reuse, no commercial-upside concern — the deliberate **opposite** of
    file-observer's AGPL-3.0 + dual-commercial (FO is a leverage product; purexml is not).
    MIT is one-way compatible with AGPL, so purexml is clean as a future FO dependency.
    **This is the pure\* family default** (purecfb, puresniff) unless a given lib has a
    specific reason to differ — flag it if so. Licensing is still a *maturity* step (don't
    rush it for a new pure\* lib just because the bearing is fixed). See `scratch/packaging_and_naming_notes.md`.
- **Posture map tracks current libexpat — the operating pattern** (set v0.5.1/v0.6).
  `RECOMMENDED_EXPAT_VERSION` = **latest-stable libexpat** and is bumped *as a patch* when
  a new DoS-fix release ships (it changes report DATA, not parse-or-block → not a LOGIC
  bump). Each attack class in `security_report().mitigations` gates on its **own** expat
  fix-version constant, **decoupled** from RECOMMENDED, so the floor can move without
  mis-gating a class. When a new libexpat DoS fix lands: (1) bump RECOMMENDED to
  latest-stable (patch); (2) if the class reaches purexml's *parse paths*, add it to the
  map gated on its fix version — a **minor** (mitigation-set change → RFC), as v0.6 did.
  This is the maintained-successor promise in mechanism; don't let the floor go stale.
  **Demonstrated twice: v0.5.1→v0.6 (2.7.4–2.8.1 train) and v0.10.1→v0.11.0 (2.8.2 batch).**
  - **Aggregate when fix versions match (v0.11):** when several CVEs share ONE fix version +
    status + nature (the 2.8.2 batch = 7 integer-overflow CVEs), map them as ONE aggregate
    class (`integer_overflow_dos_expat_2_8_2`) with the CVEs in a note — not N identical rows.
    Per-CVE classes are only for *different* fix versions (25210@2.7.4, 41080@2.8.0, 45186@2.8.1).
  - **Interim gap marker (`_HIGHEST_UNMAPPED_FIX`):** between the floor patch and the mapping
    minor, re-arm it (= the latest fix version with reachable-but-unmapped classes) so the floor
    advisory warns honestly; the mapping minor retires it again (every reachable fix tracked).
  - **Grounded-UNREACHABLE expat classes — do NOT re-map** (recorded so a future session doesn't
    "complete" them): NULL-deref CVE-2026-24515 (2.7.4, unused encoding handler) / -32776 (2.7.5,
    blocked external-param-entity); the **reentrant-handler / suspend-resume trio** CVE-2026-50219
    / -56131 / -56412 (require reentrant parser calls from a handler or suspend/resume — purexml
    does one-shot parsing only); and **xmlwf-only** CVE-2026-56409 / -56410 / -56411 (the CLI
    utility, not the library). Ground any *new* class before mapping; ground these before un-excluding.
  **Standing check (the proactive gate):** run
  `python tools/check_expat_currency.py` (tracked — runnable from any clone) — it compares the latest
  upstream libexpat release (`gh` API, no new deps) against `RECOMMENDED_EXPAT_VERSION`
  and prints IN-SYNC or DRIFT + the review checklist (exit 1 on drift). It is a
  **release-time + on-touch gate**, fired at the moments drift actually matters:
  - **before opening ANY release PR** (add it to the pre-PR Decision-gate run), and
  - **whenever a session edits `_expat_security.py`**.
  These triggers catch drift at the right time without a wall-clock poller — libexpat
  ships months apart, and the harness's recurring scheduler auto-expires in 7 days, so a
  cron would be theater here. On drift, follow the printed checklist and **surface to
  Russell — never auto-PR/merge.** Currency is now a gate, not a thing remembered.
- **CVE-2026-41080 GROUNDED + MAPPED** (v0.9, 2026-06-19 — reverses the v0.6 "deliberately
  UNMAPPED" decision, which is kept here as a tombstone). It was unmapped in v0.6 *pending
  grounding* (the grounding rule). Grounding (`scratch/review/v0.9.0_grounding_cve_2026_41080.md`)
  confirmed it is **insufficient SipHash salt entropy** (CWE-331, expat 2.8.0, LOW) and **is
  reachable** via normal name-interning — so it became the named class `hash_flooding_cve_2026_41080`,
  gated on `_HASH_FLOODING_FIXED=(2,8,0)`. Because it's a *hardening* of an existing defense
  (SipHash present below the fix, salt merely weaker), it uses the new **`EXPAT_PARTIAL`** status,
  **never `LIVE`** (bare `LIVE` would overstate). `_HIGHEST_UNMAPPED_FIX` + the generic untracked-gap
  advisory were retired (every reachable fix is now mapped). The grounding rule held: ground first,
  *then* map — and grounding determined HOW to map (PARTIAL, not LIVE). **Two-layer refinement (PR#27
  Codex, grounded vs CVE-2026-7210 / gh-149018):** full 16-byte-salt mitigation needs BOTH expat
  ≥2.8.0 AND CPython's `pyexpat` calling `XML_SetHashSalt16Bytes` (`pyexpat` sets the salt itself and
  passed only 4–8 bytes until patched). purexml can't verify the wrapper at runtime, so
  `hash_flooding` is reported **PARTIAL on every runtime** — never a version-only `MITIGATED`
  (false-green). Don't "simplify" it back to an expat-version gate.
- **The 1.0 gate is the publish-worthy ECOSYSTEM DEBUT, not one consumer** (reframed
  2026-06-17). Stress-tested by assuming file-observer gone entirely: purexml's reason to
  exist *survives the loss of any single consumer* — it's the maintained, zero-dep successor
  to the OWASP-recommended-but-abandoned `defusedxml` (0.7.1/2021; 0.8.0 stalled at rc2),
  tracking the moving libexpat threat the incumbent doesn't. So **build for a cold security
  engineer evaluating it on publish day** (the first 60 seconds), not for FO's needs. FO is
  the **anchor consumer + first validation track** (G1, alive), NOT the definition of done.
  **Publishing (PyPI publish + name-claim) stays deferred for STRATEGIC TIMING + first-impression
  quality — Russell's call — not for lack of readiness** (license is DECIDED: MIT, v0.14.1).
  Build for the first-impression
  layer. **Publish-prep progress (as of 2026-06-18):** done — public README candidate
  (`docs/PUBLIC_README_DRAFT.md`, swaps to README.md at publish), `CHANGELOG.md`,
  `COMPATIBILITY.md`, `SECURITY.md` CVE/maintenance policy, and an honest CI-gated badge row
  (python · zero-deps · stdlib · coverage≥90% · ruff · fuzzed). Remaining: `typed`
  (real annotation work — deferred, not faked), OpenSSF/Codecov (publish-gated), and the
  strategic calls (name/license/timing/disclosure channel). **Live tracker:
  `scratch/publish_prep_checklist.md`**; also `docs/ROADMAP-to-1.0.md` (Reframe note).
- **Version-assertion enforce-vs-warn: leaning INFORM-by-default** (1.0 decision, not yet
  ratified). `security_report()` informs; `assert_expat_secure()` stays opt-in. A
  hard-fail-by-default on a *moving* floor would make a consumer's gate
  environment-dependent (scanner flagged this as a determinism break) — so the lean is:
  never auto-enforce a moving floor; consumers wiring a hard gate pin the floor explicitly.
  Grounded consumer input in `scratch/version_assertion_policy_input.md`; settle at G6.

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
- **Publishing to PyPI / claiming the `purexml` name** — explicitly held for a deliberate
  strategic call (timing/first-impression). Free-name status is recorded (re-confirmed
  2026-06-27), not acted on. **Note: this no longer covers the license** — license is now
  DECIDED + APPLIED (MIT, v0.14.1); only the publish + name-claim remain held. (Cross-reference:
  Known decisions, adoption-model bullet.)
- **`defusedxml.lxml` coverage** — **excluded on zero-dep identity** (ratified 2026-06-19).
  `defusedxml.lxml` wraps the third-party `lxml` library; covering it would require depending on
  `lxml`, breaking purexml's stdlib-only, zero-runtime-dependency contract (and it's deprecated
  upstream). The usage measurement found **390 import sites** — so this is a *principled*
  exclusion, not a demand-based one. Do not "add the popular one" without re-opening: the only
  way in would be an optional non-stdlib extra, which is a different product. See
  `scratch/research/2026-06-19_defusedxml-usage-measurement.md`.
- **`pulldom` as a consumer-facing module** — deferred (measured-negligible: 48 sites). Not
  excluded — add if demand appears. (`expatbuilder` is the internal minidom engine, not exposed.)
  **`expatreader` was promoted deferred→done in v0.12** (it's the natural home for the sax engine —
  `create_parser`/`_DefusedExpatParser`), so `purexml.expatreader` now ships.

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

The four legs (all four *run* on minors+; their **depth** scales by change type — see
the **Review-tier rubric** below; patches subset per scope):

1. **In-house multi-agent swarm** — finder angles × candidates → verify →
   ranked findings. Same model, decorrelated *perspectives*.
2. **Cross-model** — a different model family from the Claude author. Run via
   `route.sh` (the orchestrator, which picks legs by heat/health) or by hand:
   **`gpt.sh`** (OpenAI, inline, read-only) is the genuinely **independent** vote —
   it does NOT collapse with the Gemini legs, so it's the one that buys *confirmation*;
   **`gem-pro.sh`** (Gemini, inline, on `agy`) adds coverage (~1 vote with any Gemini
   bot); **`gem-review.sh`** (agy + maestro, `/tmp`-snapshot-guarded) is the
   whole-codebase red-team. `static.sh` (non-LLM) + `deps.sh` (CVE) decorrelate on
   axes the LLMs miss. Old `gem.sh`/`gem-oauth.sh` were **removed** 2026-06-29.
3. **Repo-clone audit + empirical sweep** — clean-room clone; deterministic
   sweep vs a baseline.
4. **PR bots** — **CodeRabbit** (auto-review on PR open, ~15s, org-wide) is the
   current async bot. External. (Gemini Code Assist still comments but is sunsetting
   2026-07; Codex/Copilot are reserves.)

### Review-tier rubric (how the legs scale by change type)

Codified from v0.1–v0.6 practice — "subset per scope" made precise so scaling is a
**recorded standard, not silent per-PR judgment**. Pick the tier by three questions:
*(a) does it touch parse-or-block behavior (the mirror)? (b) is it a new public
capability/surface? (c) is it security-load-bearing?*

| Change type | Leg 1 (in-house) | Leg 2 (cross-model: `gpt.sh`/`gem-pro.sh` via `route.sh`) | Leg 3 (sweep) | Leg 4 (CodeRabbit) | RFC / compliance |
|---|---|---|---|---|---|
| **Feature minor** — new parse surface / capability; touches the mirror (v0.2–v0.4) | full multi-angle swarm | yes | **mandatory** | yes | RFC + compliance |
| **Report-only / additive-to-provisional minor** — no parse-or-block change (v0.6) | 1 decorrelated finder | yes (1 pass) | yes — as the cheap **"mirror-untouched" proof** (expect 0 divergences) | yes | RFC + compliance |
| **Patch** — bug fix / hardening / data within an already-approved design (v0.1.1/.2, v0.3.1, v0.5.1) | inline grounded probes or 1 finder | subset — `gpt.sh`/`gem-pro.sh` **if security-relevant**, else skip (recorded) | yes if it *could* touch the mirror | yes (on PR) | HISTORY only |
| **Docs-only** (PR #9, #12) | — | — | — | — (CI only) | — |

**Floor that never scales (holds at every tier):**
- The **grounding rule** — triage every finding against real code before it counts.
- The **empirical sweep on anything that could touch the mirror** — even report-only runs
  it to *prove* untouched (0 divergences is the evidence, not the assumption).
- **PR bots fire on every minor+** (leg 4 is on-open; it's checked at the before-merge gate).
- **Findings logged** in `scratch/review/`; **compliance before merge** on minors+.
- **Security overrides scale-down:** if a change is security-load-bearing, legs 1+2 stay at
  full depth regardless of diff size (the adversarial leg carries extra weight here — see
  *What this is*). A tiny diff to a blocking handler is a feature-minor-tier review.

**Recording rule:** state the chosen tier in the PR body / findings log (e.g. "scaled per
report-only scope — sweep as mirror-proof, single in-house finder"). Scaling **down** is a
conscious, written decision; scaling is never the thing you slide into.

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

**Documentation freshness — sweep ALL docs together, not piecemeal** (Russell,
2026-06-16). When a change warrants a doc update, refresh **every** doc to the
current state in that one pass — don't fix only the doc that prompted it. The set
to sweep: `README.md`, `CLAUDE.md` (What this is / Architecture / Spec versions /
Known decisions), `STACK.md`, `LIMITATIONS.md`, `SECURITY.md`, `PUBLIC_CONTRACT.md`,
`HISTORY.md`, `docs/ROADMAP-to-1.0.md`, `docs/FO_REQUIRED_COMPATIBILITY.md`, and the
`scratch/review/auditor_GEMINI.md` adapter. Docs drift in lockstep, so catching
them up together (one "docs: freshness sweep to vX.Y" commit) keeps them
consistent and is cheaper than chasing each later. See CONVENTIONS.md §3.2.
