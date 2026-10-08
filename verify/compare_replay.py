#!/usr/bin/env python3
"""Compare a replay's scores with the published run, overall and per category.

Usage:  python3 verify/compare_replay.py <replay results directory>
(replay_omnimemeval.sh calls it for you at the end.)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLISHED = ROOT / "results" / "beam" / "openway-beam_v2_full" / "openway_beam_grades.json"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    replay_dir = Path(sys.argv[1])
    pub = json.loads(PUBLISHED.read_text())
    new = json.loads((replay_dir / "openway_beam_grades.json").read_text())

    def row(name: str, a: float, b: float) -> None:
        print(f"{name:<28}{a * 100:>10.2f}{b * 100:>10.2f}{(b - a) * 100:>+9.2f}")

    print(f"{'':<28}{'published':>10}{'replay':>10}{'diff':>9}")
    row("overall", pub["overall"]["nugget_score_mean"], new["overall"]["nugget_score_mean"])
    for dim in sorted(pub["per_dimension"]):
        row(dim, pub["per_dimension"][dim]["nugget_score_mean"],
            new["per_dimension"].get(dim, {}).get("nugget_score_mean", float("nan")))
    print(f"\nquestions scored in the replay: {new['overall']['total_questions']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
