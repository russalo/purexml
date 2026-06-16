# Security Policy

## Scope

TODO: Describe what this project **does** and **does not** do, with security
implications. Be explicit about the trust model.

For an observation-only tool, the shape is:

> purexml is an **observation-only** tool. It reads files and emits
> metadata. It never:
> - Executes file content
> - Modifies source files
> - Opens network connections
> - Runs embedded scripts, macros, or code found in inputs

Adapt to your project. For a web service: what auth boundaries, what state
changes, what side effects. For a CLI: what it touches on the filesystem.
For a library: what surface area the host process inherits.

## Reporting Vulnerabilities

If you discover a security issue, please report it privately:

- **Email:** TODO@example.com *(replace with the project's security contact)*
- **Do not** open a public GitHub issue for security vulnerabilities

We will acknowledge receipt within {{N}} hours and provide an initial
assessment within {{N}} days. *(Russalo default: 48 hours / 7 days.)*

## Supported Versions

TODO: Replace with the project's supported-versions table. Russalo
convention: support the current minor with full backports, the previous
minor with security fixes only, anything older is unsupported (please
upgrade).

| Version | Supported |
|---|---|
| {{X.Y}}.x | Yes (current) |
| {{X.Y-1}}.x | Security fixes only |
| < {{X.Y-1}} | No |

## Dependency Security

TODO: Document the project's optional / runtime / build dependencies and
their security posture. Use a table of dependency / role / risk mitigation.
Note which deps are **optional** (with a fallback path) and which are
**required** (no fallback).

| Dependency | Role | Risk mitigation |
|---|---|---|
| TODO | TODO | TODO |

Russalo convention: optional deps gate their callers via extras; if absent,
the code path falls through gracefully or emits a documented error code.
New dependencies — especially native / parser deps — must be added with
the **bounded-observation discipline** below: every new parser path
inherits the project's existing caps, fail-closed defaults, and
degraded-record-not-crash contract.

## Bounded Observation

*Delete this section if not relevant to the project.*

TODO: If the project bounds its observation (sample reads, decompression
caps, time budgets), document the bounds here so consumers and reviewers can
verify them. Typical shape:

> All extractors operate within declared bounds:
> - **Default sample:** small fixed read from file head (e.g. 8KB)
> - **Per-format deviations:** declared and bounded (e.g. 128KB for
>   container formats that need the central directory)
> - **Decompression caps:** every decompression call gated by a wrapper
>   with a strict output cap (e.g. 64MB)
> - **Traversal validation:** path components validated against traversal
>   attacks
> - **In-tree containment:** symlinks resolving outside the source directory
>   are skipped
> - **Degraded records, not crashes:** a single unreadable input produces a
>   record + error, never an aborted run

**The discipline is universal: any new parser / IO path added to the
project must inherit these bounds.** A real cautionary tale: a new parser
path shipped without inheriting existing caps, and the red-team round had
to retrofit them — a small adversarial input that expanded to multiple
GB of RSS was caught only because the review pass specifically went
looking for places the discipline hadn't been carried through. Every new
IO surface is a place this bug class can re-emerge; the bounds are a
checklist, not a one-time setup.
