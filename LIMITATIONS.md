# Limitations

purexml reports what it can see / do, within declared bounds,
deterministically. This document states plainly what it does **not** do, so
consumers can apply their own judgment on top of its output.

## It does not make judgments

TODO: If the project surfaces observations that could be mistaken for
verdicts (security flags, classifications, quality scores), say plainly here
that they are **observations, not assessments**. Shape:

> Safety flags are **structural observations, not threat assessments**. A
> flag means "this structure was observed," not "this file is dangerous."
> purexml never quarantines, scores, or verdicts an input. Apply
> your own threat model to the observations.

## It observes within bounds — null means "not seen here," not "not present"

TODO: If the project bounds its observation (sample size, time budget,
recursion depth, byte cap), say so here and explain what `null` / missing
fields mean. Shape:

> Observation is bounded by design. A `null` or absent field means the
> signal was **not observed within those bounds** — not that it is absent
> from the source.

Typical bounds to document:
- Sample size / byte cap (e.g. "default 8KB read from file head")
- Per-format budget overrides (e.g. "OOXML deviation: 128KB")
- Whole-file caps (e.g. "structural reader capped at 64MB")
- Recursion / traversal limits

## It is not {{adjacent tool}}

TODO: Be explicit about what this project is **adjacent to** but **not**.
The principle: a project does one job well, neighbours do related jobs.
Shape:

> purexml is not a parser or full-content extractor. Specialist
> tools extract **envelopes and structural signals** on a best-effort basis
> within their budget. Does not guarantee:
> - complete or correct extraction of document bodies,
> - recovery of malformed, encrypted, or corrupt inputs,
> - OCR, ingestion, embeddings, or classification — these are downstream
>   concerns, out of scope by design.

## Threat model

TODO: Spell out the **trust model** the project assumes about its inputs.
Untrusted inputs (e.g. arbitrary files from anywhere) demand a different
bar than trusted inputs (e.g. a server's own database).

Typical entries:
- What can the input contain that we treat as adversarial?
- What attack surfaces are bounded? (decompression bombs, path traversal,
  expansion attacks, recursion limits)
- What is **out of scope** for the threat model? (e.g. supply-chain attacks
  on dependencies, side-channel timing attacks, OS-level exploits)
- Where do degraded records replace crashes? (the never-crash contract — a
  single bad input produces a degraded output record + error, never an
  aborted run)

## Accepted limitations

TODO: List documented residuals — known false-positives / false-negatives /
edge cases the project deliberately accepts rather than chasing endlessly.
The discipline is to **enumerate accepted limitations** rather than let
them rot as unrecorded gaps. Each entry should say:

- What the limitation is
- Why it's accepted (cost / scope / data-gated / not worth fixing yet)
- What would change to revisit it (a corpus exists, a dep is available, a
  hypothesis validates)

Shape:

> **{{limitation name}}** — {{one-line description of the edge case}}.
> Accepted: {{cost / scope reason}}. Revisit when {{condition that would
> change the calculus}}.
