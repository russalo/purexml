# {{project_name}} Version History

This is the running index of all versions, their specifications, and their
compliance reports. Use this as the **entry point** when orienting on the
project — it's the one document where every release leaves a row.

**Current version:** see the project's version source-of-truth (e.g.
`pyproject.toml`, the `VERSION` constant, or `go.mod`) and the latest entry
below.

**How to read this index:**
- Active versions have specs and compliance reports in `docs/`.
- Archived versions have specs and compliance reports under `docs/archive/`
  (convention: at the first major bump, the previous major's RFCs and
  compliance reports move into `docs/archive/{previous_major}.x/`).
- Pre-1.0 versions use **looser formatting** — narrative entries, no
  compliance report requirement, RFCs optional. Once the project ships 1.0
  the row shape below becomes mandatory; the public contract binds at the
  same time.

---

## Versions

| Version | Schema | Date | Notable | Spec | Compliance |
|---|---|---|---|---|---|
| 0.1.0 | n/a | YYYY-MM-DD | TODO: one-line summary of what this release adds / fixes. Note version-axis changes (e.g. SCHEMA n/a → 0.1; LOGIC introduced). | _(no RFC — pre-1.0 looser formatting)_ | _(no compliance report)_ |
| 1.0.0 | 1.0 | YYYY-MM-DD | **Schema freeze.** Public contract binding. Backward compatibility policy in effect. No new features — governance declaration on a validated codebase. | [v1.0.0_RFC_Specification.md](docs/v1.0.0_RFC_Specification.md) | [COMPLIANCE-v1.0.md](docs/COMPLIANCE-v1.0.md) |
| 1.0.1 | 1.0 | YYYY-MM-DD | **Patch release** — example shape. Bug fix in {component}. SCHEMA unchanged. _(part of v1.0; HISTORY only, no RFC.)_ | _(no RFC — patch)_ | _(part of v1.0)_ |

---

## Drafts in Flight

TODO: List any RFCs currently in draft (`docs/v{X.Y.Z}_RFC_DRAFT.md`). When
none are open, state so explicitly rather than deleting the section — the
empty-but-named state is the signal:

> No drafts in flight.

---

## Historical Drafts and Design Documents

These are working documents from earlier in the project. Kept for design
history; not specifications themselves. Pre-RFC scratch material (early
design notes, alternate drafts) lives here once promoted out of `scratch/`.

| File | Era | Purpose |
|---|---|---|
| TODO | Pre-vX.Y | TODO: short description of what this is |

---

## Compliance Report Gaps

TODO: Note any versions that did **not** get a compliance report and why
(usually patch releases — they're covered by HISTORY narrative + the
parent minor's compliance report). Default rule:

> Patches inherit their parent minor's compliance report; their narrative
> lives in this index, not in a separate report.
