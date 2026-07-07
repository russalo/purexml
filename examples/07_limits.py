"""07 — Opt-in structural-DoS caps (Limits): default-off, so the mirror is unchanged.

defusedxml (and expat's own amplification cap) don't bound *structural* DoS —
pathological-but-legal input like a 100k-deep tree or an attribute flood. purexml
adds opt-in caps: pass `limits=`. With no limits the default is byte-equivalent to
defusedxml, so the drop-in promise is never violated.

Run:  python examples/07_limits.py
"""
from purexml import Limits, RECOMMENDED_LIMITS, fromstring
from purexml.errors import AttributesExceeded, DepthExceeded, LimitExceeded


def main() -> None:
    print("RECOMMENDED_LIMITS:", RECOMMENDED_LIMITS)

    deep = "<a>" * 2000 + "</a>" * 2000

    # WITHOUT limits: a deep document parses (default = strict defusedxml mirror).
    print("no limits  -> depth-2000 parses:", fromstring(deep).tag)

    # WITH RECOMMENDED_LIMITS: refused at the parse boundary with a typed,
    # catchable DepthExceeded (a LimitExceeded, which is a ValueError).
    try:
        fromstring(deep, limits=RECOMMENDED_LIMITS)
        raise AssertionError("deep doc was not capped")  # regression tripwire
    except DepthExceeded as e:
        print("RECOMMENDED -> blocked:", e)

    # Custom caps — tune for your own trust budget.
    tight = Limits(max_depth=5, max_attributes=3, max_bytes=1_000_000)
    try:
        fromstring("<e a='1' b='2' c='3' d='4'/>", limits=tight)
        raise AssertionError("attribute flood was not capped")  # regression tripwire
    except AttributesExceeded as e:
        print("custom     -> blocked:", e)

    # All caps raise a LimitExceeded subclass (and thus a ValueError).
    assert issubclass(DepthExceeded, LimitExceeded)
    assert issubclass(LimitExceeded, ValueError)


if __name__ == "__main__":
    main()
