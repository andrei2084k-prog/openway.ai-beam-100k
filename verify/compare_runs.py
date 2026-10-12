#!/usr/bin/env python3
"""Compare the two independent runs question by question.

No API key, no third-party packages. Both runs used the same OpenWay.ai code
and configuration, the same harness commit, data and models; each wrote its
memory from scratch. This script checks that the runs answered the same 400
questions (same question, reference answer and rubric), then prints:

* each run's score and the mean of the two runs, with standard error and a
  bootstrap 95% interval over questions;
* the paired difference run 2 − run 1 with its bootstrap 95% interval, and how
  many questions scored the same, higher or lower;
* the spread one run carries on its own: the standard deviation of a single
  run's total, estimated from the per-question differences;
* the score per category in each run;
* how different the two runs' memory blocks are: the share of lines two blocks
  for the same question have in common (the first line, today's date, is left
  out). Memory is written by a language model, so two runs never write the
  same lines; low overlap means the second run did not reuse the first.

Usage:  python3 verify/compare_runs.py
"""

from __future__ import annotations

import json
import random
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ("beam_v2_full", "beam_v2_full_r2")  # run 1 (7 Oct 2026), run 2 (11 Oct 2026)


def load(run: str, name: str) -> dict[tuple[str, int], dict]:
    data = json.loads((ROOT / "results" / "beam" / f"openway-{run}" / name).read_text())
    return {(r["conv_id"], r["question_idx"]): r for qs in data.values() for r in qs}


def summary(xs: list[float]) -> tuple[float, float, float, float]:
    rng = random.Random(0)
    boot = sorted(st.mean(rng.choices(xs, k=len(xs))) for _ in range(10_000))
    return st.mean(xs), st.pstdev(xs) / len(xs) ** 0.5, boot[249], boot[9_749]


def lines(block: str) -> set[str]:
    return {ln.strip() for ln in block.splitlines()[1:] if ln.strip() and not ln.lstrip().startswith("#")}


def main() -> int:
    judged = {run: load(run, "openway_beam_judged.json") for run in RUNS}
    search = {run: load(run, "openway_beam_search_results.json") for run in RUNS}
    a, b = RUNS
    keys = list(judged[a])  # file order, as recompute_score.py reads it

    problems = []
    if set(judged[a]) != set(judged[b]):
        problems.append("the runs scored different questions")
    for k in keys:
        ra, rb = judged[a][k], judged.get(b, {}).get(k)
        if rb is None:
            continue
        for field in ("question", "golden_answer", "rubric", "dimension"):
            if ra[field] != rb[field]:
                problems.append(f"{k}: {field} differs between the runs")
    if problems:
        print("FAIL")
        for p in problems[:20]:
            print("  -", p)
        return 1

    score = {run: [judged[run][k]["nugget_score"] * 100 for k in keys] for run in RUNS}
    print(f"questions in both runs: {len(keys)} (same question, reference answer and rubric)\n")
    print(f"{'':<16}{'score':>8}{'SE':>7}   bootstrap 95%")
    own_order = {run: [r["nugget_score"] * 100 for r in judged[run].values()] for run in RUNS}
    for name, xs in (("run 1", own_order[a]), ("run 2", own_order[b]),
                     ("mean of the two", [(x + y) / 2 for x, y in zip(score[a], score[b])])):
        m, se, lo, hi = summary(xs)
        print(f"{name:<16}{m:>8.2f}{se:>7.2f}   {lo:.2f}–{hi:.2f}")

    diff = [y - x for x, y in zip(score[a], score[b])]
    m, se, lo, hi = summary(diff)
    print(f"\nrun 2 − run 1   : {m:+.2f} (bootstrap 95% {lo:+.2f} to {hi:+.2f})")
    print(f"per question    : {sum(d == 0 for d in diff)} the same, {sum(d > 0 for d in diff)} higher, "
          f"{sum(d < 0 for d in diff)} lower")
    single = se / 2 ** 0.5
    print(f"one run's spread: ±{single:.2f} (standard deviation of a single run's total); two runs of the same "
          f"code are expected to land within ±{1.96 * se:.1f} of each other 95% of the time")

    print(f"\n{'category':<28}{'run 1':>8}{'run 2':>8}{'mean':>8}{'diff':>8}{'n':>5}")
    for dim in sorted({judged[a][k]["dimension"] for k in keys}):
        idx = [i for i, k in enumerate(keys) if judged[a][k]["dimension"] == dim]
        x, y = st.mean(score[a][i] for i in idx), st.mean(score[b][i] for i in idx)
        print(f"{dim:<28}{x:>8.2f}{y:>8.2f}{(x + y) / 2:>8.2f}{y - x:>+8.2f}{len(idx):>5}")

    overlap = []
    for k in keys:
        la, lb = lines(search[a][k]["search_context"]), lines(search[b][k]["search_context"])
        overlap.append(len(la & lb) / len(la | lb) if la | lb else 1.0)
    same = sum(search[a][k]["search_context"] == search[b][k]["search_context"] for k in keys)
    print(f"\nmemory blocks   : {same} of {len(keys)} identical; median share of lines in common "
          f"{st.median(overlap):.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
