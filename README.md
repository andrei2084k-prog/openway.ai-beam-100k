# OpenWay.ai memory on BEAM-100K — complete run outputs

This repository holds every output of one complete run of **OpenWay.ai's memory** on the **BEAM-100K** long-term memory benchmark, scored with the **OmniMemEval** harness on 7 October 2026.

It is here so that anyone can check how the score was obtained. Every claim below can be checked with the scripts in [`verify/`](verify/):
- four checks need nothing but Python 3;
- two re-run the benchmark's answer and judge steps with your own OpenAI key, for about $1.

## Result

**72.06 nugget score** on 400 of 400 questions.
- **Uncertainty:** standard error ±1.76; bootstrap 95% interval 68.59–75.50.
- **Failures:** none at search, answer or judge.
- **Context size:** on average 4,247 tokens per question reached the answer model — the answer prompt plus the memory block.

| Category | What it tests | Score | Questions |
|---|---|---:|---:|
| preference_following | answers respect the user's preferences | 96.25 | 40 |
| instruction_following | answers follow instructions the user gave earlier | 91.25 | 40 |
| abstention | says so when something was never discussed | 85.00 | 40 |
| information_extraction | recalls specific facts | 84.22 | 40 |
| summarization | summarizes what happened across sessions | 79.03 | 40 |
| multi_session_reasoning | combines facts from different sessions | 69.17 | 40 |
| contradiction_resolution | notices two incompatible statements | 67.50 | 40 |
| temporal_reasoning | computes dates and durations | 58.75 | 40 |
| knowledge_update | gives the latest value after changes | 56.88 | 40 |
| event_ordering | restores the order of events | 32.51 | 40 |

**How a question is scored (nugget score):**
- Each reference answer is split into rubric items.
- The judge scores every item 1 (covered), 0.5 (partly covered) or 0 (not covered).
- A question's score is the mean over its items.
- Event-ordering questions are scored by Kendall tau-b against the reference order.
- The total is the mean over the 400 questions, × 100.

### For context: the OmniMemEval table

The other systems' numbers are OmniMemEval's own reproduced results under the same protocol: same answer model, judge, prompts and questions. The source is [`docs/user_memory/results.md` at commit `0b1ea8d`](https://github.com/MemTensor/OmniMemEval/blob/0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d/docs/user_memory/results.md).

The OpenWay.ai row is **this run**, made by us with the same harness. It is not part of OmniMemEval's published table.

| System | BEAM-100K | Context tokens per question |
|---|---:|---:|
| **OpenWay.ai (this run)** | **72.06** | **4,247** |
| Viking | 70.76 | 2,023 |
| Mem0 | 70.41 | 1,055 |
| Hindsight | 70.22 | 24,085 |
| Letta | 69.22 | 82,013 |
| Zep / Graphiti | 68.70 | 8,667 |
| MemOS | 66.87 | 1,636 |
| Supermemory | 65.98 | 6,294 |
| mem9 | 65.75 | 5,372 |
| MemMachine | 64.80 | 5,413 |
| Cognee | 59.30 | 33,065 |
| EverOS | 58.64 | 7,393 |

**Each score carries about ±1.8 of standard error.** Differences between neighbouring rows of a couple of points are within that noise.

## How the run was done

**Harness.** [MemTensor/OmniMemEval](https://github.com/MemTensor/OmniMemEval) at commit `0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d`. Its answer, judge, metric and report steps were run as published. Its ingestion and search steps reach the memory backend through `add()` and `search()`, as they do for every system.

**How OpenWay.ai was connected.** OpenWay.ai was plugged in as a memory backend, the way the harness connects every system, through two calls:
- `add()` gives memory one session of a conversation;
- `search()` returns, for a question, the memory block that OpenWay.ai's assistant receives at the start of a turn.

In the harness, OpenWay.ai is registered under the library name `openway`. That is why the results are in `openway-beam_v2_full/` and named `openway_beam_*`, and why the harness's own report and configuration say `openway`.

**Data.** BEAM-100K:
- 20 conversations, 90 sessions, 2,866 assistant turns, 400 questions (40 per category);
- the file is [`data/beam_100k.json`](data/beam_100k.json), as produced by the harness's `data/beam/prepare_beam.py`;
- SHA-256 `613b85b9e5eca98b88de25bedb7490f1dbf61ae4c361d544452feea19bfa18a3`.

**Models.**
- Answers: `gpt-4.1-mini-2025-04-14`, the harness's own answer prompt.
- Judge: `gpt-4o-mini-2024-07-18`, the harness's own judge prompts, one judge run per item.
- Both at temperature 0.

**`top_k`.** The harness passes `top_k=20`. OpenWay.ai returns its own fixed-budget block whatever `top_k` is, so its size shows up in the context-token column instead.

### Things you will see in the data

1. **Dates.**
   - Every session was given to memory with its date from the dataset: the session's time anchor, for example `March-15-2024`.
   - For each conversation, memory's "today" was the day after that conversation's last session.
   - It is the first line of every memory block: `Today is …`.
2. **Consolidation before the questions.**
   - After the last session and before the first question, memory finished its background consolidation: session summaries and the user's profile.
   - In the product this runs on its own after conversations.
   - The order is recorded in [`run/timeline.json`](run/timeline.json):
     - ingestion ended at 18:51:16 UTC;
     - consolidation ended at 18:55:59;
     - the first question was read at 18:56:26.
3. **No language model sees the question on OpenWay.ai's side.** During the search phase OpenWay.ai made **0 language-model calls**. The only calls were 631 embedding calls.
4. **Memory blocks are published verbatim,** exactly as the answer model received them.
   - They contain OpenWay.ai's own framing for its assistant: section headings, the current date, and a line asking to follow rules the user set.
   - In 35 of 400 blocks, memory held two statements that cannot both be true. There the block carries the product's instruction to give both, each with its date, and ask which holds.
   - Those 35 blocks span 9 categories, and only 5 of them are contradiction_resolution questions.
5. **The judge is a language model and errs in both directions.** Its reason for every verdict is published unmodified. [`verify/show_question.py`](verify/show_question.py) prints it next to the answer, so any single verdict can be checked by eye.

## What is in this repository

| Path | What it is |
|---|---|
| `results/beam/openway-beam_v2_full/openway_beam_search_results.json` | For each of the 400 questions: the question, reference answer, rubric, and the **memory block OpenWay.ai returned** (`search_context`) |
| `results/beam/openway-beam_v2_full/openway_beam_responses.json` | The answer model's answer to each question |
| `results/beam/openway-beam_v2_full/openway_beam_judged.json` | The judge's verdict and reason for every rubric item, and each question's score |
| `results/beam/openway-beam_v2_full/openway_beam_grades.json`, `openway_beam_results.xlsx` | The harness's totals by category, difficulty and scale |
| `results/beam/openway-beam_v2_full/exp_report.md`, `experiment_config.sh` | The harness's own report and the configuration it recorded |
| `results/beam/openway-beam_v2_full/*_status.json`, `success_records.txt`, `token_usage_*.json`, `openway_beam_ingestion_stats.json` | Per-stage status, sessions ingested, answer and judge token usage, ingestion timings |
| `data/beam_100k.json` | The BEAM-100K dataset the run used: conversations, questions, reference answers, rubrics |
| `run/timeline.json` | When each phase ran, its model-call counts, and two ordering checks |
| `run/ingestion_sessions.jsonl` | One line per ingested session: conversation, session, dataset date, assistant turns, start and end time |
| `verify/` | The scripts below |
| `MANIFEST.sha256` | SHA-256 of every file |

The `results/` directory has the harness's own layout. You can drop it into an OmniMemEval checkout as is.

## How to verify

Requirements: Python 3.10+. Steps 5 and 6 also need `git`, network access and an OpenAI API key.

**1. Nothing was changed after publication.**
```bash
python3 verify/check_manifest.py
```

**2. The score follows from the judge's verdicts.**
```bash
python3 verify/recompute_score.py
```
It recomputes every question's score from the per-item verdicts, then the totals, and compares them with the harness's grades file. Expected output: `overall : 72.06 (SE ±1.76, bootstrap 95% 68.59–75.50)` and `PASS`.

**3. The memory blocks do not carry the reference answers.**
```bash
python3 verify/leak_check.py
```
It searches all 400 blocks for:
- the reference answer verbatim;
- any rubric item of 25+ characters;
- the abstention reference phrase.

Then it traces every match. Expected output:
- no abstention phrase;
- 14 short verbatim matches. Each is either said in that conversation itself (12) or a paraphrase of the user's words that sits in most blocks of that conversation whatever the question (2).

**4. Read any question end to end.**
```bash
python3 verify/show_question.py --list          # all 400: conversation, question, category, score
python3 verify/show_question.py 8 11            # question, reference, memory block, answer, verdicts
```

**5. Re-judge our answers with your own key** (harness steps 4–6, about $0.15, a few minutes).
```bash
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh judge
```

**6. Re-answer from our memory blocks, then judge** (harness steps 3–6, about $1.2, about 10 minutes).
```bash
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh answer
```

**What steps 5 and 6 do:**
- clone OmniMemEval at the run's commit into `.replay/`;
- add the name `openway` to the harness's list of libraries. Its answer, judge and metric steps only check that the name is known and never call a memory backend;
- run the harness's own scripts on the published blocks;
- print your scores next to ours.

Both models run at temperature 0, but OpenAI models are not bit-for-bit deterministic, so expect close scores, not identical ones.

Step 6 is the strongest check here. It takes only what OpenWay.ai's memory returned and lets you score it under the benchmark's protocol with your own account.

## License and attribution

**`data/` and `results/`** contain the BEAM dataset and material derived from it: questions, reference answers, rubrics, conversation content recalled in memory blocks. They are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), the license of BEAM. See [`LICENSE-DATA.md`](LICENSE-DATA.md).

**BEAM:** M. Tavakoli et al., *Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs*, ICLR 2026.
- [arXiv:2510.27246](https://arxiv.org/abs/2510.27246)
- [github.com/mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM)
- [huggingface.co/datasets/Mohammadta/BEAM](https://huggingface.co/datasets/Mohammadta/BEAM)

**OmniMemEval** (Apache-2.0) is not included. `verify/replay_omnimemeval.sh` clones it from its own repository.

**The scripts in `verify/`** are released under the MIT license. See [`LICENSE`](LICENSE).
