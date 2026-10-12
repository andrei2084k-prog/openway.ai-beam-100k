#!/usr/bin/env python3
"""Show one question end to end: the question, the reference answer, the
memory block the answer model received, its answer, and the judge's verdict
on every rubric item with the judge's own reason.

No API key, no third-party packages.

Usage:
  python3 verify/show_question.py 7 11        # conversation 7, question 11
  python3 verify/show_question.py --list      # every question: key, category, score
  python3 verify/show_question.py 7 11 --no-context   # skip the memory block
  python3 verify/show_question.py 7 11 --run beam_v2_full_r2   # the same question in run 2
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ("beam_v2_full", "beam_v2_full_r2")  # run 1 (7 Oct 2026), run 2 (11 Oct 2026)


def load(results: Path, name: str) -> dict[str, dict]:
    data = json.loads((results / name).read_text())
    return {r["key"]: r for qs in data.values() for r in qs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("conversation", nargs="?")
    ap.add_argument("question", nargs="?", type=int)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--no-context", action="store_true")
    ap.add_argument("--run", choices=RUNS, default=RUNS[0], help="which run (default: the first)")
    args = ap.parse_args()
    results = ROOT / "results" / "beam" / f"openway-{args.run}"

    judged = load(results, "openway_beam_judged.json")
    if args.list:
        for key, r in sorted(judged.items(), key=lambda kv: (int(kv[1]["conv_id"]), kv[1]["question_idx"])):
            print(f"{r['conv_id']:>3} {r['question_idx']:>3}  {r['dimension']:<26} {r['nugget_score']:.2f}  {r['question'][:70]}")
        return 0
    if args.conversation is None or args.question is None:
        ap.print_usage()
        return 2

    match = [r for r in judged.values()
             if r["conv_id"] == str(args.conversation) and r["question_idx"] == args.question]
    if not match:
        print("no such question", file=sys.stderr)
        return 1
    r = match[0]
    search = load(results, "openway_beam_search_results.json")[r["key"]]

    print(f"{r['key']} · {r['dimension']} · difficulty {r['difficulty']} · score {r['nugget_score']:.2f}")
    print("\n== QUESTION\n" + r["question"])
    print("\n== REFERENCE ANSWER\n" + r["golden_answer"])
    if not args.no_context:
        print(f"\n== MEMORY BLOCK ({len(search['search_context'])} characters)\n" + search["search_context"])
    print("\n== ANSWER (gpt-4.1-mini)\n" + r["answer"])
    print("\n== JUDGE (gpt-4o-mini)")
    if r["scoring_method"] == "per_rubric_item":
        for it in r["rubric_item_scores"]:
            print(f"- [{it['item_score']:.1f}] {it['rubric_item']}")
            for reason in it.get("run_reasons", []):
                print(f"      {reason}")
    else:
        print(f"{r['scoring_method']}: {r['run_scores']}  {r.get('run_reasons')}")
        print(f"rubric (expected order): {r['rubric']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
