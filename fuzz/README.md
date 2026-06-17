# Coverage-guided fuzzing (dev-only, opt-in)

The **always-run** durability gate is the *seeded* differential fuzz in
[`tests/test_fuzz_equivalence.py`](../tests/test_fuzz_equivalence.py) — it needs
no extra dependency and runs in CI on every Python in the matrix.

This directory holds the **on-demand, coverage-guided** counterpart
([`fuzz_equivalence.py`](fuzz_equivalence.py)), driven by
[Atheris](https://github.com/google/atheris) (libFuzzer). It explores parser
states the seeded generator never enumerates, holding the same invariant:
**purexml is C14N-equal-or-both-raise vs the `defusedxml` oracle** for every
input.

Atheris is **dev-only** — declared under the `[fuzz]` extra, never a runtime
dependency, never imported under `src/`. (Atheris needs a clang/libFuzzer
toolchain; it is intentionally *not* in the always-run `[dev]` set or CI.)

## Run

```sh
pip install -e '.[fuzz]'
python fuzz/fuzz_equivalence.py -atheris_runs=2000000   # bounded run
python fuzz/fuzz_equivalence.py fuzz/corpus/            # replay/seed a corpus
```

## On a finding

A divergence aborts with the offending input. Per the project's **grounding
rule**, triage it against the real code first: reconstruct the input, confirm the
break is real (not a fuzzer artifact), *then* fix. Add the minimized input to the
seeded gate so the regression is caught without Atheris next time.
