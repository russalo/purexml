# purexml Conventions

This project has two kinds of conventions:

- **Internal conventions** — how *we* keep the project consistent. Naming,
  version bump rules, document promotion paths, tracking inventories. These
  exist for the contributors, not for users.
- **Public contracts** — what *consumers* of the project's output / API can
  count on. These live in [`PUBLIC_CONTRACT.md`](PUBLIC_CONTRACT.md) (if the
  project has a stable public surface).

This document covers the **internal** conventions.

---

## 1. Versioned Concerns

A project may carry **multiple independent version axes**. They are
independent — bumping one does not require bumping the others. Pick the
axes that apply to this project; common ones:

### 1.1 RELEASE_VERSION (mandatory)
**What it is:** Package / binary release version (semver).
**Where it lives:** the language's standard manifest (`pyproject.toml`,
`go.mod`, `package.json`, …) + a constant in code + the project's CLI / API
metadata.
**When it bumps:** Any release.
**Format:** `MAJOR.MINOR.PATCH`
**Current:** TODO

### 1.2 LOGIC_VERSION *(optional — for projects with routing / decision logic)*
**What it is:** Version of the *decision logic* — code that decides how an
input gets routed / classified / processed. Independent of the surface API.
**When it bumps:** Any time the same input would be routed / processed
differently than before.
**Format:** `MAJOR.MINOR.PATCH`. May lag RELEASE_VERSION.
**Internal rule:** When in doubt, bump it. Stale LOGIC_VERSION causes silent
reproducibility bugs across environments.

### 1.3 SCHEMA_VERSION *(optional — for projects that emit / consume a stable schema)*
**What it is:** Version of the output / wire-format shape — what fields
exist, how they nest, what they're named.
**When it bumps:**
- MINOR: additive changes (new fields, new namespaces).
- MAJOR: breaking changes (removal, rename, type change).
- No bump on patch releases.
**Format:** `MAJOR.MINOR` (no patch).
**Public contract:** Yes — this is what consumers depend on.

### 1.4 Bump Consistency Rule

When RELEASE_VERSION bumps, all version surfaces update together: the
manifest file, the in-code constant, any version string in module
docstrings / banners, test version assertions. A version-surface sync guard
test prevents silent drift.

---

## 2. Version-Bump Rules (when to bump which axis)

| Change | RELEASE | LOGIC | SCHEMA |
|---|---|---|---|
| Bug fix, same I/O | PATCH | unchanged | unchanged |
| Internal refactor, same output | PATCH | unchanged | unchanged |
| Routing / decision changes | MINOR | bump | unchanged unless field shape moves |
| New additive output field | MINOR | unchanged (unless logic also moved) | MINOR |
| Promote provisional → stable | MINOR | unchanged | MINOR (contract change) |
| Rename / remove / retype output field | MAJOR | usually bump | MAJOR |
| Performance change, byte-identical output | PATCH or MINOR | **unchanged** | unchanged |

The last row is load-bearing: a performance feature whose output is
byte-identical (e.g. parallel workers) keeps LOGIC + SCHEMA frozen — that
unchanged-ness is the falsifiable contract.

---

## 3. Document Promotion Path

```
[idea]
  ↓
[scratch/ note]                       informal, subject to change, gitignored
  ↓
[docs/v{X}.Y.Z_RFC_DRAFT.md]          formal proposal, under review
  ↓
[approval]
  ↓
[docs/v{X}.Y.Z_RFC_Specification.md]  approved, frozen
  ↓
[implementation on v{X}.Y.Z branch]
  ↓
[docs/COMPLIANCE-v{X}.Y.md]           audit against the spec
  ↓
[PR review + merge to main]
  ↓
[stable in main, version released]
```

**Internal rule:** Don't skip stages. Don't approve a draft without renaming.
Don't merge an implementation without compliance. Don't release without tests
passing.

**The RFC-for-minors-only rule:** Patch releases (vX.Y.Z, Z>0) do not get an
RFC or a compliance report. Their narrative lives in
[`HISTORY.md`](HISTORY.md) only. The design was already approved in the
parent minor's RFC; patches are bug fixes / hardening within that envelope.

### 3.1 Field stability ladder (candidate → provisional → stable)

For projects with a public schema, fields graduate through tiers:

- **candidate** *(below provisional)* — a held observation tracked + measured
  in the review apparatus (e.g. a corpus sweep), **not in the public
  output**. No contract status. Promote → provisional when the held reason
  is resolved and the harvest shows the signal is worth surfacing.
- **provisional** — in the output, "may change in a MINOR." Bar that doesn't
  relax: deterministic, never-crash, bounded for any new parser path.
- **stable** — under the backward-compat policy; not removable / retypable
  without a MAJOR bump.

A field enters at **candidate or provisional, never directly stable.**
Promotion criterion: *settled producing logic + evidence of value*, not age.

### 3.2 Documentation freshness sweeps (catch up ALL docs together)

When a change warrants updating docs, **sweep every doc to the current state in
that one pass** — never patch only the doc that prompted it. The docs drift in
lockstep (a shipped version touches the surface description, the version index,
the scope/limitations, the security scope, the roadmap), so updating them together
keeps them consistent and is cheaper than chasing each one later. Land it as a
single `docs: freshness sweep to vX.Y` commit.

The sweep set: `README.md`, `CLAUDE.md` (What this is / Architecture / Spec
versions / Known decisions), `STACK.md`, `LIMITATIONS.md`, `SECURITY.md`,
`PUBLIC_CONTRACT.md`, `HISTORY.md`, `docs/ROADMAP-to-1.0.md`,
`docs/FO_REQUIRED_COMPATIBILITY.md`, and the `scratch/review/auditor_GEMINI.md` adapter.
(Established 2026-06-16.)

---

## 4. File-Naming Conventions

### 4.1 RFC Specifications

- **Approved:** `docs/v{X.Y.Z}_RFC_Specification.md`. Status field
  `**Status:** Approved`. Title does NOT contain "(DRAFT)".
- **Draft:** `docs/v{X.Y.Z}_RFC_DRAFT.md`. Status `**Status:** Draft`. Title
  contains "(DRAFT)". May be edited / restructured / deleted.
- **Promotion:** rename file (drop `_DRAFT`, add `_Specification`), remove
  "(DRAFT)" from title, change Status.

### 4.2 Compliance Reports

`docs/COMPLIANCE-v{X.Y}.md` — one per minor with a corresponding RFC.
Audits implementation against approved RFC requirements. Tabular:
requirement, implementation location, status. Created **after**
implementation, **before** PR merge.

### 4.3 Versioned Output Artifacts

If the project emits versioned artifacts (manifests, reports, exports),
follow the pattern: `{kind}_v{VERSION}_{timestamp}.{ext}`. Example:
`{{artifact_kind}}_v{X.Y.Z}_{YYYY-MM-DDThhmm}.{ext}`. The version in the
filename is the **producer's RELEASE_VERSION** at emit time.

### 4.4 Scratch / Working Notes

`scratch/` (gitignored):
- Descriptive names.
- Version-targeted files use `v{X.Y}_` prefix when tied to a future release.
- Subject to revision / deletion.
- Promote to `docs/` when stable (one-way).

### 4.5 Per-Project Review Notes

`scratch/review/` (gitignored):
- Per-release audit logs (Gemini findings, swarm output, sweep diffs).
- Project-specific auditor adapter (`auditor_GEMINI.md`, filled from
  `auditor_GEMINI.skeleton.md` in review-kit).
- Findings markdown (`v{X.Y}_*_findings.md`).
- Treat the same as `scratch/` — promote anything durable into `docs/`.

---

## 5. Code Review Apparatus (four legs)

The originating principle: *a reviewer's value is its decorrelation from
the author.* An AI that wrote the code is biased toward it, and its own
tests share its blind spots. Review must come from where the author didn't
think.

### 5.1 The four legs (run all on minors+; subset on patches per scope)

1. **In-house multi-agent swarm** — finder angles × candidates → verify →
   ranked findings. Same model, **decorrelated perspectives**. The angle
   structure is the reusable IP; realize via a self-spawned agent swarm if
   the bundled skill is gated.
2. **Gemini cross-model** — different model family. Two modes:
   - **(a) inline prompt** — `gem.sh` / `gem-oauth.sh`, read-only,
     self-contained (inline the diff; do NOT ask Gemini to read files — a
     headless run hangs scanning the workspace). Best for **pre-PR diff
     review**.
   - **(b) native review skills** — `gem-review.sh` /
     `gem-review-oauth.sh` → `/code-review`, `/maestro:security-audit`.
     Tool-using (yolo, `/tmp`-snapshot-guarded). Best for **whole-codebase
     red-teams**.
3. **Repo-clone audit + empirical sweep** — clean-room clone of the repo;
   a deterministic sweep vs a baseline (corpus diff, golden diff, fixture
   diff). Catches what the test suite doesn't: real-world data drift,
   detection regressions, byte-equality breaks.
4. **PR bots** — Codex / Gemini Code Assist / Copilot on PR open.
   External.

### 5.2 Canonical tooling

[`/srv/projects/review-kit/`](file:///srv/projects/review-kit/) is the
shared kit. **Per-project copies** live in `scratch/review/` (this
project's gitignored review surface), along with:

- The filled-in auditor adapter (`auditor_GEMINI.md`).
- This project's corpus sweep / golden harness.
- Findings logs per release.
- Any project-specific threat-model overlays (see
  `overlay_public_web.md` for the shape if the project faces the open
  internet).

### 5.3 The `.review-canonical` marker

The repo root carries an empty `.review-canonical` file. This is the
**primary tripwire** for the yolo-mode review wrappers — they refuse to run
anywhere but a disposable `/tmp` snapshot, and the marker tells the snapshot
which copy is canonical. The marker travels with the repo via git; treat it
as load-bearing.

### 5.4 Grounding rule (non-negotiable)

Triage every cross-model / bot finding against the real code before it
counts. Construct the failing input, confirm it's real, *then* fix. Models
overstate severity and critique code they were never shown. Expect a
typical cross-model pass to surface a mix of real findings and findings
that evaporate under repro — the grounding step is what separates the two.

---

## 6. PR Conventions

1. **Title:** `v{VERSION}: {short description}`.
2. **Body must include:** summary by phase, test count change, schema
   version statement (if applicable), test plan checklist.
3. **Compliance report committed before merge** (not follow-up) — for
   minors+.
4. **All review comments addressed before merge.**
5. **Branch deleted after merge.**

---

## 7. Internal Tracking Inventory

This section is for **us**. The running list of everything the project has.
Keep it current — projects fill these in as inventories accumulate.

### Public API surface (top-level `purexml`, all re-exported)

The frozen-at-1.0 *mirror* surface vs the PROVISIONAL *defense-in-depth*:

| Name | Kind | Since | Freeze posture |
|---|---|---|---|
| `fromstring`, `parse`, `iterparse`, `fromstringlist`, `XML`, `XMLParser`, `tostring`, `ParseError` | ElementTree family (also at `purexml.ElementTree`) | v0.1–v0.3 | STABLE (mirror) |
| `PureXMLError`, `DTDForbidden`, `EntitiesForbidden`, `ExternalReferenceForbidden` | exception hierarchy | v0.1–v0.2 | STABLE (mirror) |
| `Limits`, `RECOMMENDED_LIMITS`, `LimitExceeded`, `DepthExceeded`, `AttributesExceeded`, `SizeExceeded` | opt-in structural-DoS caps | v0.4 | PROVISIONAL |
| `EXPAT_VERSION`, `SAFE_EXPAT_VERSION`, `RECOMMENDED_EXPAT_VERSION`, `expat_is_secure`, `assert_expat_secure` | libexpat version awareness | v0.1.2 | PROVISIONAL |
| `security_report`, `SecurityReport`, `BLOCKED`, `EXPAT_MITIGATED`, `OPT_IN`, `LIVE` | posture report (trust surface) | v0.5 | PROVISIONAL |

Source of truth: `src/purexml/__init__.py` `__all__` (a test asserts version sync;
keep this table in step when exports change). Freeze postures: `docs/ROADMAP-to-1.0.md`.

### Versioned constants
- RELEASE: `pyproject.toml` `version` + `purexml.__version__` (test-synced).
- LOGIC (mitigation set): narrated per release in `HISTORY.md`. SCHEMA: n/a (returns stdlib `Element`).

Remaining TODO subsections (delete what doesn't apply): error codes, configuration
profiles, closed tables — none accumulated yet beyond the surface above.

---

## 8. When This Document Updates

This is a living reference. Update it at the same time as the code change,
not as a follow-up. Update when:

- A new versioned concern is introduced.
- A new specialist / namespace / signature / flag / error code is added.
- Naming conventions change.
- A new document type is introduced.
- A promotion path stage is added.
