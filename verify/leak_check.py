#!/usr/bin/env python3
"""Check that the memory blocks do not carry the benchmark's reference answers.

No API key, no third-party packages. For each of the 400 questions it looks
at the memory block the answer model received and reports:

* the reference answer appearing verbatim in the block;
* any rubric item (25+ characters, with the "LLM response should …" prefix
  removed) appearing verbatim in the block;
* the abstention reference phrase ("Based on the provided chat, there is no
  information …") anywhere in the block.

Every verbatim match is then traced: is the same text present in that
conversation's own transcript (then memory legitimately recalled it), and in
what share of that conversation's 20 blocks does it appear? Text shown in most
blocks of a conversation is part of what memory shows for that user whatever
the question (a profile line, a session summary), not something picked for
the question. A match is explained by either.

Text is compared case-insensitively with whitespace collapsed.

Usage:  python3 verify/leak_check.py                  # run 1
        python3 verify/leak_check.py --run beam_v2_full_r2   # run 2
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ("beam_v2_full", "beam_v2_full_r2")  # run 1 (7 Oct 2026), run 2 (11 Oct 2026)
DATA = ROOT / "data" / "beam_100k.json"
MIN_LEN = 25
PREFIX = re.compile(r"^LLM response should (contain|state|mention):\s*", re.I)
ABSTENTION = ("based on the provided chat", "there is no information related")


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", choices=RUNS, default=RUNS[0], help="which run (default: the first)")
    results = ROOT / "results" / "beam" / f"openway-{ap.parse_args().run}"
    search = json.loads((results / "openway_beam_search_results.json").read_text())
    rows = [r for qs in search.values() for r in qs]

    transcripts = {}
    for line in DATA.read_text().splitlines():
        if line.strip():
            conv = json.loads(line)
            transcripts[str(conv["conversation_id"])] = norm(
                " ".join(m["content"] for sess in conv["chat"] for m in sess)
            )

    blocks_by_conv: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        blocks_by_conv[r["conv_id"]].append(norm(r["search_context"]))

    gold_hits = rubric_hits = abstention_hits = 0
    matches = []
    for r in rows:
        block = norm(r["search_context"])
        if any(p in block for p in ABSTENTION):
            abstention_hits += 1
        gold = norm(r["golden_answer"])
        if len(gold) >= MIN_LEN and gold in block:
            gold_hits += 1
            matches.append((r, "reference answer", gold))
        for item in r["rubric"]:
            text = norm(PREFIX.sub("", item))
            if len(text) >= MIN_LEN and text in block:
                rubric_hits += 1
                matches.append((r, "rubric item", text))

    print(f"blocks checked                              : {len(rows)}")
    print(f"abstention reference phrase in a block      : {abstention_hits}")
    print(f"reference answer verbatim in a block        : {gold_hits}")
    print(f"rubric item verbatim in a block             : {rubric_hits}")
    print()

    unexplained = 0
    for r, kind, text in matches:
        in_transcript = text in transcripts[r["conv_id"]]
        blocks = blocks_by_conv[r["conv_id"]]
        shown = sum(text in b for b in blocks)
        if not (in_transcript or shown * 2 > len(blocks)):
            unexplained += 1
        print(f"- {r['key']} [{r['dimension']}] {kind}: \"{text[:90]}\"")
        print(f"    in the conversation's transcript: {'yes' if in_transcript else 'no'}"
              f" · in {shown}/{len(blocks)} blocks of this conversation")

    print()
    if abstention_hits or unexplained:
        print(f"REVIEW — {abstention_hits} abstention phrase(s), {unexplained} match(es) not explained by the transcript")
        return 1
    print("PASS — no reference phrasing in any block; every verbatim match is either said in the "
          "conversation itself or shown in most blocks of that conversation, whatever the question")
    return 0


if __name__ == "__main__":
    sys.exit(main())
