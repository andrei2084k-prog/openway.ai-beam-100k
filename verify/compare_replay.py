#!/usr/bin/env python3
"""Compare a replay's scores with the published run, overall and per category.

Usage:  python3 verify/compare_replay.py <replay results directory> [--run beam_v2_full_r2]
(replay_omnimemeval.sh calls it for you at the end.)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ("beam_v2_full", "beam_v2_full_r2", "beam_v3_full")  # runs 1, 2 (7, 11 Oct 2026), run 3 (16 Oct)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("replay_dir", type=Path)
    ap.add_argument("--run", choices=RUNS, default=RUNS[0], help="the published run it replays (default: the first)")
    args = ap.parse_args()
    replay_dir = args.replay_dir
    published = ROOT / "results" / "beam" / f"openway-{args.run}" / "openway_beam_grades.json"
    pub = json.loads(published.read_text())
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
