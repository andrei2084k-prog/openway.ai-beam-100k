# OmniMemEval Experiment Report — openway-beam_v2_full

> Generated: 2026-10-07 19:06:18

## Experiment Configuration

| Parameter | Value |
|-----------|-------|
| Benchmark | BEAM |
| Memory Framework | openway |
| Version | beam_v2_full |
| Run Time | 2026-10-07 18:56:15 UTC |
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
| Results Directory | `results/beam/openway-beam_v2_full` |

**Reproduce:**

```bash
./scripts/run_beam_eval.sh --replay results/beam/openway-beam_v2_full
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
| Context Tokens (avg) | 4246.9 |

## Evaluation Results

### Overall Scores

| Metric | Score |
|--------|-------|
| Nugget Score | 0.7206 ± 0.3526 |
| Questions | 400 |

### By Conversation Scale

| Scale | Nugget Score | Questions |
|-------|-------------|-----------|
| 100k | 0.7206 ± 0.3526 | 400 |

### By Question Dimension

| Dimension | Nugget Score | Questions |
|-----------|-------------|-----------|
| abstention | 0.8500 ± 0.2784 | 40 |
| contradiction_resolution | 0.6750 ± 0.2088 | 40 |
| event_ordering | 0.3251 ± 0.2327 | 40 |
| information_extraction | 0.8422 ± 0.2881 | 40 |
| instruction_following | 0.9125 ± 0.2342 | 40 |
| knowledge_update | 0.5687 ± 0.4643 | 40 |
| multi_session_reasoning | 0.6917 ± 0.3739 | 40 |
| preference_following | 0.9625 ± 0.1192 | 40 |
| summarization | 0.7903 ± 0.1726 | 40 |
| temporal_reasoning | 0.5875 ± 0.4456 | 40 |

### By Difficulty

| Difficulty | Nugget Score | Questions |
|------------|-------------|-----------|
| clear | 0.6750 ± 0.2088 | 40 |
| easy | 0.6402 ± 0.4211 | 124 |
| hard | 0.8582 ± 0.1974 | 42 |
| medium | 0.7519 ± 0.3412 | 193 |

### Pipeline Status

| Stage | Failed Units | Skipped Records | Status Counts |
|-------|--------------|-----------------|---------------|
| search | 0 | 0 | success=400 |
| answer | 0 | 0 | success=400 |
| eval | 0 | 0 | success=400 |

### Latency Metrics

| Metric | Avg (ms) | P50 (ms) | P95 (ms) |
|--------|----------|----------|----------|
| Add Latency | 363410.3 | 337859.4 | 590472.0 |
| Search Latency | 753.1 | 719.1 | 1155.9 |
