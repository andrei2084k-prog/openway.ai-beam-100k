# OmniMemEval Experiment Report — openway-beam_v3_full

> Generated: 2026-10-16 11:44:20

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Benchmark | BEAM |
| Memory Framework | openway |
| Version | beam_v3_full |
| Run Time | 2026-10-16 11:37:04 UTC |
| Git | `unknown` (unknown) |
| WORKERS | 6 |
| LLM_WORKERS | 10 |
| TOPK | 20 |
| SCALE | 100k |
| NUM_RUNS | 1 |
| SAVE_MODEL_INPUT | 0 |
| CLEAR | 0 |
| WAIT_AFTER_INGEST | 0 |
| STREAMING | 0 |
| START_IDX | 0 |
| END_IDX |  |
| ALLOW_EMPTY_SEARCH | 1 |
| SKIP_FAILED_SEARCH | 0 |
| SKIP_FAILED_ANSWER | 0 |
| SKIP_FAILED_JUDGE | 0 |
| SKIP_FAILED_STREAMING | 0 |
| Results Directory | `results/beam/openway-beam_v3_full` |

**Reproduce:**

```bash
./scripts/run_beam_eval.sh --replay results/beam/openway-beam_v3_full
```

### Environment Variables (snapshot_eval.env)

| Variable | Value |
|----------|-------|
| `ANSWER_MODEL` | `gpt-4.1-mini-2025-04-14` |
| `EVAL_MODEL` | `gpt-4o-mini-2024-07-18` |

## Context Tokens

> Context Tokens are answer-stage prompt/input tokens. They are used as an approximate proxy for retrieved search-result length and should be compared only under the same benchmark, answer model, and prompt template.

| Metric | Value |
|--------|-------|
| Answer Model | gpt-4.1-mini-2025-04-14 |
| Answer API Calls | 400 |
| Context Tokens (avg) | 5366.1 |

## Evaluation Results

### Overall Scores

| Metric | Score |
|--------|-------|
| Nugget Score | 0.7507 ± 0.3394 |
| Questions | 400 |

### By Conversation Scale

| Scale | Nugget Score | Questions |
|-------|-------------|-----------|
| 100k | 0.7507 ± 0.3394 | 400 |

### By Question Dimension

| Dimension | Nugget Score | Questions |
|-----------|-------------|-----------|
| abstention | 0.8875 ± 0.2368 | 40 |
| contradiction_resolution | 0.6594 ± 0.2218 | 40 |
| event_ordering | 0.4104 ± 0.2700 | 40 |
| information_extraction | 0.8599 ± 0.2469 | 40 |
| instruction_following | 0.9500 ± 0.1785 | 40 |
| knowledge_update | 0.6062 ± 0.4773 | 40 |
| multi_session_reasoning | 0.7207 ± 0.3762 | 40 |
| preference_following | 0.9375 ± 0.1556 | 40 |
| summarization | 0.8375 ± 0.1940 | 40 |
| temporal_reasoning | 0.6375 ± 0.4219 | 40 |

### By Difficulty

| Difficulty | Nugget Score | Questions |
|------------|-------------|-----------|
| clear | 0.6594 ± 0.2218 | 40 |
| easy | 0.6754 ± 0.4169 | 124 |
| hard | 0.8596 ± 0.2078 | 42 |
| medium | 0.7938 ± 0.3123 | 193 |

### Pipeline Status

| Stage | Failed Units | Skipped Records | Status Counts |
|-------|--------------|-----------------|---------------|
| search | 0 | 0 | success=400 |
| answer | 0 | 0 | success=400 |
| eval | 0 | 0 | success=400 |

### Latency Metrics

| Metric | Avg (ms) | P50 (ms) | P95 (ms) |
|--------|----------|----------|----------|
| Add Latency | 350942.9 | 319968.1 | 590305.1 |
| Search Latency | 729.0 | 665.8 | 1145.3 |
