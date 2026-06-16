# purexml Public Contract

> **If your project has no stable public surface, delete this file.** Examples
> of "no public surface": internal scripts, experiments, prototypes, services
> with no documented external API. Examples of "has a public surface": a
> library other projects import, a CLI other projects script against, a
> server with a documented HTTP contract, a tool that emits a documented
> output format.

This document defines what **consumers** of purexml's output / API
can rely on. It is the stability commitment from purexml to
downstream systems.

> **This contract is binding as of v{X.0}.** The stability commitments below
> are obligations, not intentions. Fields / endpoints marked stable will not
> be removed, renamed, or change type without a MAJOR version bump. See the
> backward compatibility and deprecation policies below.

---

## 1. What Consumers Can Count On

### 1.1 Schema / API Version

TODO: Describe the version axis(es) consumers depend on. Typical shape:

> Every {output / response} includes a top-level `schema_version` field in
> the format `MAJOR.MINOR`.
>
> **Stability rules (post-v{X.0}):**
> - **MINOR bumps are additive only.** New fields may appear. Existing
>   fields will not be removed, renamed, or change type.
> - **MAJOR bumps are reserved for breaking changes** and require an
>   explicit migration path. A MAJOR bump will be preceded by at least one
>   full MINOR version of deprecation warnings on affected fields.
> - **Consumers should branch on the MAJOR version.** Code written for
>   schema 1.x will continue to work with schema 1.y where y > x.

### 1.2 Stable Top-Level Surface

TODO: Tabulate the stable top-level keys / endpoints / functions and their
types.

| Key / Endpoint / Function | Type | Stability |
|---|---|---|
| TODO | TODO | **Stable** — always present |

### 1.3 Stable Per-Record / Per-Field Structure

TODO: If the project emits records (manifest entries, response objects,
etc.), document the stable field list here. Mark each field's stability
explicitly (**Stable** / **Provisional** / **Candidate**).

| Field | Type | Stability |
|---|---|---|
| TODO | TODO | **Stable** |

### 1.4 Namespaces / Tool Names / Registries

TODO: If the project uses namespacing (specialist namespaces, MIME types,
tool registries), document which namespace keys are stable and what they
contain.

---

## 2. What Counts as a Breaking Change

A change is **breaking** (and requires a MAJOR bump) if:

- A stable field / endpoint is removed.
- A stable field is renamed.
- A stable field changes type.
- A stable field's semantic contract changes (e.g. units, encoding,
  meaning).
- A required input becomes incompatible (a previously-valid input is now
  rejected).

A change is **additive** (and ships in a MINOR) if:

- A new field appears alongside the existing ones.
- A new endpoint / tool / namespace appears.
- A new optional input is accepted.
- A field that was always null gains a value (filling nulls is additive —
  see the schema-bump conventions covered in
  [`CONVENTIONS.md`](CONVENTIONS.md)).

### 2.1 Deprecation Policy

TODO: Document the deprecation policy. Typical russalo shape:

> A field destined for removal in v{N+1}.0 must be marked deprecated in at
> least one full v{N}.MINOR release before removal, with a deprecation
> warning visible to consumers (in the docs, in the output where possible,
> in `HISTORY.md`).

### 2.2 Provisional Fields

Fields marked **Provisional** in §1 are **not under the stable contract**.
They MAY change in any MINOR release. Consumers depending on a provisional
field should pin to a specific MINOR or be ready to adapt.

The provisional → stable promotion criterion is *settled producing logic +
evidence of value*. Promotions ship in a MINOR and are recorded in
[`HISTORY.md`](HISTORY.md) and [`CONVENTIONS.md`](CONVENTIONS.md) §3.1.

The full ladder is `candidate → provisional → stable`. **Candidate** fields
are tracked outside the manifest (in sweep/instrumentation artifacts), never
emitted in the public output, and exist to gather evidence cheaply before
the project commits to a provisional field that carries a contract cost.
See [`CONVENTIONS.md`](CONVENTIONS.md) §3.1 for the registry.

---

## 3. What Consumers Should NOT Count On

TODO: Be explicit about what is **not** under the contract. Typical entries:

- **Internal version axes** (e.g. LOGIC_VERSION) — visible in output for
  diagnosis, but not a stability commitment. We bump them freely.
- **Import paths / package layout** — refactors that preserve the public
  output / API are not contract changes.
- **Error message wording** — error *codes* are stable, error *messages*
  are not.
- **Performance characteristics** — we may change algorithms (workers,
  caching, sampling) as long as the output is byte-identical.
- **Ordering of optional fields / iteration order** unless explicitly
  documented as stable.

---

## 4. Backward Compatibility Policy

TODO: Spell out the project's compatibility guarantee. Typical shape:

> Within a MAJOR version, code that works on v{X}.Y will continue to work
> on v{X}.Z where Z > Y. Tests that pinned to v{X}.Y output will pass on
> v{X}.Z output for the *stable* fields (additive fields may need new
> assertions).

---

## 5. Version of This Contract

TODO: When did this contract become binding? Link the release that froze it.

> This contract became binding at v{X.0} (YYYY-MM-DD). See
> [`HISTORY.md`](HISTORY.md) for the freeze entry.
