<!-- Vulnerability fixes follow SECURITY.md (private), not a public PR. -->

## What & why

<!-- What changed and the reason. Link the issue you discussed for non-trivial changes. -->

## Checklist

- [ ] `python -m pytest tests/ -q` passes (and adds a falsify-first test for new behavior)
- [ ] `ruff check src tests` clean · `mypy src` (`--strict`) clean · coverage ≥ 90%
- [ ] **Default parse behavior unchanged** — any new strictness is opt-in, default-off
      (the differential-fuzz equivalence gate stays at 0 divergences)
- [ ] **Zero new runtime deps**; nothing under `src/` imports network/filesystem/subprocess
      (the `tests/test_no_io.py` guard still passes)
- [ ] Docs that drift with this change are updated in the same PR (README / CHANGELOG /
      COMPATIBILITY / LIMITATIONS as applicable)

## Notes

<!-- Anything reviewers should know: scope decisions, edges, follow-ups. -->
