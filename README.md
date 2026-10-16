# OpenWay.ai memory on BEAM-100K — complete run outputs

This repository holds every output of three complete runs of **OpenWay.ai's memory** on the **BEAM-100K** long-term memory benchmark, scored with the **OmniMemEval** harness on 7, 11 and 16 October 2026. Runs 1 and 2 used the same code; the second was made to check that the score repeats. Run 3 used a newer version of OpenWay.ai's code.

It is here so that anyone can check how the score was obtained. Every claim below can be checked with the scripts in [`verify/`](verify/):
- five checks need nothing but Python 3;
- two re-run the benchmark's answer and judge steps with your own OpenAI key, for about $1 per run.

## Result

| | Run 1 | Run 2 | Mean of runs 1–2 | Run 3 (newer code) |
|---|---:|---:|---:|---:|
| Date | 7 October 2026 | 11 October 2026 | | 16 October 2026 |
| **Nugget score** | **72.06** | **71.96** | **72.01** | **75.07** |
| Standard error | ±1.76 | ±1.79 | ±1.66 | ±1.70 |
| Bootstrap 95% interval | 68.59–75.50 | 68.45–75.37 | 68.73–75.24 | 71.77–78.35 |
| Context tokens per question | 4,247 | 4,219 | 4,233 | 5,366 |

- **Questions:** 400 of 400 in each run.
- **Failures:** none at search, answer or judge, in any run.
- **Context tokens:** on average, what reached the answer model per question — the answer prompt plus the memory block.

| Category | What it tests | Run 1 | Run 2 | Mean of runs 1–2 | Run 3 | Questions |
|---|---|---:|---:|---:|---:|---:|
| preference_following | answers respect the user's preferences | 96.25 | 94.38 | 95.31 | 93.75 | 40 |
| instruction_following | answers follow instructions the user gave earlier | 91.25 | 91.88 | 91.56 | 95.00 | 40 |
| abstention | says so when something was never discussed | 85.00 | 91.25 | 88.12 | 88.75 | 40 |
| information_extraction | recalls specific facts | 84.22 | 87.45 | 85.83 | 85.99 | 40 |
| summarization | summarizes what happened across sessions | 79.03 | 76.90 | 77.97 | 83.75 | 40 |
| multi_session_reasoning | combines facts from different sessions | 69.17 | 66.45 | 67.81 | 72.07 | 40 |
| contradiction_resolution | notices two incompatible statements | 67.50 | 64.06 | 65.78 | 65.94 | 40 |
| temporal_reasoning | computes dates and durations | 58.75 | 57.50 | 58.12 | 63.75 | 40 |
| knowledge_update | gives the latest value after changes | 56.88 | 56.25 | 56.56 | 60.62 | 40 |
| event_ordering | restores the order of events | 32.51 | 33.46 | 32.98 | 41.04 | 40 |

**How a question is scored (nugget score):**
- Each reference answer is split into rubric items.
- The judge scores every item 1 (covered), 0.5 (partly covered) or 0 (not covered).
- A question's score is the mean over its items.
- Event-ordering questions are scored by Kendall tau-b against the reference order.
- The total is the mean over the 400 questions, × 100.

### Does the score repeat?

This section is about runs 1 and 2, which used the same code. Run 3 used a newer version of the code and is a single run.

**What was the same in both runs:**
- OpenWay.ai's code and configuration;
- the harness commit, the dataset file, the answer and judge models, the protocol.

**What was not:**
- Each run started from an empty memory and wrote it again from the conversations.
- Memory is written by a language model, so the two runs wrote different memories:
  - none of the 400 memory blocks is the same in both runs;
  - two blocks for the same question have a median of 33% of their lines in common.

**How far apart the runs landed:**
- Run 2 − run 1 = **−0.10** points (bootstrap 95% interval −2.59 to +2.34).
- Question by question, 264 of 400 scored the same, 63 higher and 73 lower.
- The per-question differences put one run's own spread at **±0.89**. At that spread, two runs of the same code land within ±2.5 of each other 95% of the time; these two landed 0.10 apart.
- Single categories move more, up to 6.25 points (abstention). Each category has only 40 questions, so that is within its noise.

[`verify/compare_runs.py`](verify/compare_runs.py) prints all of the above from the published files.

**One change on our side between the runs:**
- The adapter that feeds the harness's sessions into OpenWay.ai gained support for BEAM's larger scales.
- With it, the adapter stopped applying the product's per-workspace cap on profile-merge model calls. In the product the cap is 200 calls a day, and a benchmark that replays months of conversation in two hours can reach it.
- In run 2 no conversation needed more than 158 such calls, so the cap would not have changed run 2's outcome.

### For context: the OmniMemEval table

The other systems' numbers are OmniMemEval's own reproduced results under the same protocol: same answer model, judge, prompts and questions. The source is [`docs/user_memory/results.md` at commit `0b1ea8d`](https://github.com/MemTensor/OmniMemEval/blob/0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d/docs/user_memory/results.md).

The OpenWay.ai row is **our latest run, run 3**, made by us with the same harness on a newer version of our code; runs 1 and 2 scored 72.06 and 71.96. It is not part of OmniMemEval's published table.

| System | BEAM-100K | Context tokens per question |
|---|---:|---:|
| **OpenWay.ai (run 3)** | **75.07** | **5,366** |
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

## How the runs were done

All three runs were done the same way.

**Harness.** [MemTensor/OmniMemEval](https://github.com/MemTensor/OmniMemEval) at commit `0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d`. Its answer, judge, metric and report steps were run as published. Its ingestion and search steps reach the memory backend through `add()` and `search()`, as they do for every system.

**How OpenWay.ai was connected.** OpenWay.ai was plugged in as a memory backend, the way the harness connects every system, through two calls:
- `add()` gives memory one session of a conversation;
- `search()` returns, for a question, the memory block that OpenWay.ai's assistant receives at the start of a turn.

In the harness, OpenWay.ai is registered under the library name `openway`. That is why the results are in `openway-beam_v2_full/` (run 1), `openway-beam_v2_full_r2/` (run 2) and `openway-beam_v3_full/` (run 3) and named `openway_beam_*`, and why the harness's own report and configuration say `openway`.

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
   - The order is recorded in [`run/timeline.json`](run/timeline.json) for run 1, [`run/beam_v2_full_r2/timeline.json`](run/beam_v2_full_r2/timeline.json) for run 2 and [`run/beam_v3_full/timeline.json`](run/beam_v3_full/timeline.json) for run 3:

     | | Run 1 (7 Oct) | Run 2 (11 Oct) | Run 3 (16 Oct) |
     |---|---|---|---|
     | Ingestion ended | 18:51:16 UTC | 22:14:53 UTC | 11:31:58 UTC |
     | Consolidation ended | 18:55:59 | 22:19:31 | 11:36:49 |
     | First question read | 18:56:26 | 22:19:56 | 11:37:15 |
3. **No language model sees the question on OpenWay.ai's side.** During the search phase OpenWay.ai made **0 language-model calls** in either run. The only calls were embedding calls: 631 in run 1, 568 in run 2, 568 in run 3.
4. **Memory blocks are published verbatim,** exactly as the answer model received them.
   - They contain OpenWay.ai's own framing for its assistant: section headings, the current date, and a line asking to follow rules the user set.
   - Some blocks hold two statements from memory that cannot both be true. There the block carries the product's instruction to give both, each with its date, and ask which holds.
   - Run 1 has 35 such blocks out of 400. They span 9 categories, and only 5 of them are contradiction_resolution questions.
   - Run 2 has 24 such blocks. They span 8 categories, and 9 of them are contradiction_resolution questions.
   - Run 3 has 34 such blocks. They span 10 categories, and 8 of them are contradiction_resolution questions.
5. **The judge is a language model and errs in both directions.** Its reason for every verdict is published unmodified. [`verify/show_question.py`](verify/show_question.py) prints it next to the answer, so any single verdict can be checked by eye.

## What is in this repository

Run 1 is in `results/beam/openway-beam_v2_full/` and `run/`. Run 2 is in `results/beam/openway-beam_v2_full_r2/` and `run/beam_v2_full_r2/`. Run 3 is in `results/beam/openway-beam_v3_full/` and `run/beam_v3_full/`. Each run has the same set of files:

| Path (run 1; runs 2 and 3 have the same names) | What it is |
|---|---|
| `results/beam/openway-beam_v2_full/openway_beam_search_results.json` | For each of the 400 questions: the question, reference answer, rubric, and the **memory block OpenWay.ai returned** (`search_context`) |
| `results/beam/openway-beam_v2_full/openway_beam_responses.json` | The answer model's answer to each question |
| `results/beam/openway-beam_v2_full/openway_beam_judged.json` | The judge's verdict and reason for every rubric item, and each question's score |
| `results/beam/openway-beam_v2_full/openway_beam_grades.json`, `openway_beam_results.xlsx` | The harness's totals by category, difficulty and scale |
| `results/beam/openway-beam_v2_full/exp_report.md`, `experiment_config.sh` | The harness's own report and the configuration it recorded |
| `results/beam/openway-beam_v2_full/*_status.json`, `success_records.txt`, `token_usage_*.json`, `openway_beam_ingestion_stats.json` | Per-stage status, sessions ingested, answer and judge token usage, ingestion timings |
| `run/timeline.json` | When each phase ran, its model-call counts, and two ordering checks |
| `run/ingestion_sessions.jsonl` | One line per ingested session: conversation, session, dataset date, assistant turns, start and end time |

Shared by all runs:

| Path | What it is |
|---|---|
| `data/beam_100k.json` | The BEAM-100K dataset all runs used: conversations, questions, reference answers, rubrics |
| `verify/` | The scripts below |
| `MANIFEST.sha256` | SHA-256 of every file |

The `results/` directory has the harness's own layout. You can drop it into an OmniMemEval checkout as is.

## How to verify

Requirements: Python 3.10+. Steps 6 and 7 also need `git`, network access and an OpenAI API key.

Steps 2, 3, 4, 6 and 7 check run 1 by default. Add `--run beam_v2_full_r2` or `--run beam_v3_full` (for steps 6 and 7, the word `beam_v2_full_r2` or `beam_v3_full` after the mode) to check run 2 or run 3.

**1. Nothing was changed after publication.**
```bash
python3 verify/check_manifest.py
```

**2. The score follows from the judge's verdicts.**
```bash
python3 verify/recompute_score.py
python3 verify/recompute_score.py --run beam_v2_full_r2
python3 verify/recompute_score.py --run beam_v3_full
```
It recomputes every question's score from the per-item verdicts, then the totals, and compares them with the harness's grades file. Expected output, then `PASS`:
- run 1: `overall : 72.06 (SE ±1.76, bootstrap 95% 68.59–75.50)`;
- run 2: `overall : 71.96 (SE ±1.79, bootstrap 95% 68.45–75.37)`;
- run 3: `overall : 75.07 (SE ±1.70, bootstrap 95% 71.77–78.35)`.

**3. The memory blocks do not carry the reference answers.**
```bash
python3 verify/leak_check.py
python3 verify/leak_check.py --run beam_v2_full_r2
python3 verify/leak_check.py --run beam_v3_full
```
It searches all 400 blocks for:
- the reference answer verbatim;
- any rubric item of 25+ characters;
- the abstention reference phrase.

Then it traces every match. Expected output:
- no abstention phrase, in either run;
- run 1: 14 short verbatim matches. Each is either said in that conversation itself (12) or a paraphrase of the user's words that sits in most blocks of that conversation whatever the question (2);
- run 2: 15 short verbatim matches. Each is either said in that conversation itself (12) or text that sits in most blocks of that conversation whatever the question (3);
- run 3: 17 short verbatim matches. Each is either said in that conversation itself (15) or text that sits in most blocks of that conversation whatever the question (2).

**4. Read any question end to end.**
```bash
python3 verify/show_question.py --list          # all 400: conversation, question, category, score
python3 verify/show_question.py 8 11            # question, reference, memory block, answer, verdicts
python3 verify/show_question.py 8 11 --run beam_v2_full_r2   # the same question in run 2
```

**5. Compare the two runs.**
```bash
python3 verify/compare_runs.py
```
It checks that both runs answered the same 400 questions, with the same reference answers and rubrics. Then it prints the numbers in [Does the score repeat?](#does-the-score-repeat):
- each run's score, and the mean of the two;
- the paired difference and the per-question counts;
- one run's own spread;
- the categories;
- how much the two runs' memory blocks have in common.

**6. Re-judge our answers with your own key** (harness steps 4–6, about $0.15, a few minutes).
```bash
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh judge                    # run 1
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh judge beam_v2_full_r2    # run 2
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh judge beam_v3_full       # run 3
```

**7. Re-answer from our memory blocks, then judge** (harness steps 3–6, about $1.2, about 10 minutes).
```bash
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh answer                   # run 1
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh answer beam_v2_full_r2   # run 2
OPENAI_API_KEY=sk-... verify/replay_omnimemeval.sh answer beam_v3_full      # run 3
```

**What steps 6 and 7 do:**
- clone OmniMemEval at the run's commit into `.replay/`;
- add the name `openway` to the harness's list of libraries. Its answer, judge and metric steps only check that the name is known and never call a memory backend;
- run the harness's own scripts on the published blocks;
- print your scores next to ours.

Both models run at temperature 0, but OpenAI models are not bit-for-bit deterministic, so expect close scores, not identical ones.

Step 7 is the strongest check here. It takes only what OpenWay.ai's memory returned and lets you score it under the benchmark's protocol with your own account.

## License and attribution

**`data/` and `results/`** contain the BEAM dataset and material derived from it: questions, reference answers, rubrics, conversation content recalled in memory blocks. They are released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), the license of BEAM. See [`LICENSE-DATA.md`](LICENSE-DATA.md).

**BEAM:** M. Tavakoli et al., *Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs*, ICLR 2026.
- [arXiv:2510.27246](https://arxiv.org/abs/2510.27246)
- [github.com/mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM)
- [huggingface.co/datasets/Mohammadta/BEAM](https://huggingface.co/datasets/Mohammadta/BEAM)

**OmniMemEval** (Apache-2.0) is not included. `verify/replay_omnimemeval.sh` clones it from its own repository.

**The scripts in `verify/`** are released under the MIT license. See [`LICENSE`](LICENSE).
