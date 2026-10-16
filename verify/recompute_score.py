#!/usr/bin/env python3
"""Recompute the BEAM-100K score from the judge's per-item verdicts.

No API key, no third-party packages. Checks three things:

1. every question's score follows from the judge's verdicts
   (per-rubric-item questions: mean of the item scores; event-ordering
   questions: mean of the Kendall tau-b run scores);
2. the overall and per-category means match what OmniMemEval wrote in
   ``openway_beam_grades.json``;
3. prints the standard error and a bootstrap 95% interval of the mean.

Usage:  python3 verify/recompute_score.py                  # run 1
        python3 verify/recompute_score.py --run beam_v2_full_r2   # run 2
"""

from __future__ import annotations

import argparse
import json
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ("beam_v2_full", "beam_v2_full_r2", "beam_v3_full")  # runs 1, 2 (7, 11 Oct 2026), run 3 (16 Oct)
TOL = 1e-9


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", choices=RUNS, default=RUNS[0], help="which run (default: the first)")
    results = ROOT / "results" / "beam" / f"openway-{ap.parse_args().run}"
    judged = json.loads((results / "openway_beam_judged.json").read_text())
    grades = json.loads((results / "openway_beam_grades.json").read_text())
    rows = [r for qs in judged.values() for r in qs]

    problems = []
    scores: list[float] = []
    by_dim: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r.get("status") != "success":
            problems.append(f"{r['key']}: status {r.get('status')!r}")
            continue
        if r["scoring_method"] == "per_rubric_item":
            items = r["rubric_item_scores"]
            for it in items:
                if abs(st.mean(it["run_scores"]) - it["item_score"]) > TOL:
                    problems.append(f"{r['key']}: item score does not follow from its runs")
            derived = st.mean(it["item_score"] for it in items)
        else:
            derived = st.mean(r["run_scores"])
        if abs(derived - r["nugget_score"]) > TOL:
            problems.append(f"{r['key']}: stored {r['nugget_score']} != derived {derived}")
        scores.append(r["nugget_score"])
        by_dim[r["dimension"]].append(r["nugget_score"])

    n = len(scores)
    mean = st.mean(scores)
    se = st.pstdev(scores) / n ** 0.5

    rng = random.Random(0)
    boot = sorted(st.mean(rng.choices(scores, k=n)) for _ in range(10_000))
    lo, hi = boot[249], boot[9_749]

    print(f"questions scored : {n}")
    print(f"overall          : {mean * 100:.2f}  (SE ±{se * 100:.2f}, bootstrap 95% {lo * 100:.2f}–{hi * 100:.2f})")
    print()
    print(f"{'category':<28}{'score':>8}{'n':>5}")
    for dim in sorted(by_dim):
        s = by_dim[dim]
        print(f"{dim:<28}{st.mean(s) * 100:>8.2f}{len(s):>5}")
    print()

    if abs(grades["overall"]["nugget_score_mean"] - mean) > TOL:
        problems.append(f"overall {mean} != grades file {grades['overall']['nugget_score_mean']}")
    for dim, s in by_dim.items():
        ref = grades["per_dimension"][dim]["nugget_score_mean"]
        if abs(ref - st.mean(s)) > TOL:
            problems.append(f"{dim}: {st.mean(s)} != grades file {ref}")

    if problems:
        print("FAIL")
        for p in problems[:20]:
            print("  -", p)
        return 1
    print("PASS — every question's score follows from the judge's verdicts, and the totals match the grades file")
    return 0


if __name__ == "__main__":
    sys.exit(main())
