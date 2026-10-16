#!/usr/bin/env bash
# Re-run OmniMemEval's own steps on a run's published outputs, with YOUR OpenAI key.
#
#   verify/replay_omnimemeval.sh judge  [run]  # re-judge our 400 answers        (steps 4-6, ~$0.15)
#   verify/replay_omnimemeval.sh answer [run]  # re-answer from our memory blocks, then judge (steps 3-6, ~$1.2)
#
# [run] is beam_v2_full (run 1, the default), beam_v2_full_r2 (run 2) or beam_v3_full (run 3).
#
# What it does:
#   1. clones MemTensor/OmniMemEval at the exact commit the run used (into .replay/, gitignored);
#   2. adds the name "openway" to the harness's library list — its answer, judge and metric
#      steps only check that --lib is a known name; they never call a memory backend;
#   3. copies the published memory blocks (and, for "judge", the published answers) into a
#      fresh results directory of that clone;
#   4. runs the harness's own scripts: beam_responses.py, beam_eval.py, beam_metric.py,
#      with gpt-4.1-mini-2025-04-14 for answers and gpt-4o-mini-2024-07-18 as judge;
#   5. prints the replay's scores next to the published ones.
#
# Both models run at temperature 0, but OpenAI models are not bit-for-bit deterministic,
# so expect scores close to the published ones, not identical.
#
# Needs: git, python3 (3.10+), network access, OPENAI_API_KEY in the environment.
# Your key is written only to .replay/replay.env (mode 600) for the duration of the run
# and deleted on exit.

set -euo pipefail

MODE="${1:-}"
case "$MODE" in
    answer|judge) ;;
    *) sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
RUN="${2:-beam_v2_full}"
case "$RUN" in
    beam_v2_full|beam_v2_full_r2|beam_v3_full) ;;
    *) echo "unknown run: $RUN (beam_v2_full, beam_v2_full_r2 or beam_v3_full)" >&2; exit 2 ;;
esac
: "${OPENAI_API_KEY:?set OPENAI_API_KEY to your OpenAI API key}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/.replay"
OMNI="$WORK/OmniMemEval"
OMNI_REPO="https://github.com/MemTensor/OmniMemEval.git"
OMNI_COMMIT="0b1ea8d28aa2d3e03ac4a6aee17b3006a131da7d"
SRC="$ROOT/results/beam/openway-$RUN"
VERSION="replay_${MODE}_${RUN}_$(date -u +%Y%m%dT%H%M%SZ)"
DEST="$OMNI/results/beam/openway-$VERSION"
ENV_FILE="$WORK/replay.env"

mkdir -p "$WORK"
trap 'rm -f "$ENV_FILE"' EXIT

# 1. the harness at the run's commit
if [ ! -d "$OMNI/.git" ]; then
    git clone --quiet "$OMNI_REPO" "$OMNI"
fi
git -C "$OMNI" cat-file -e "$OMNI_COMMIT^{commit}" 2>/dev/null || git -C "$OMNI" fetch --quiet origin
git -C "$OMNI" checkout --quiet --force "$OMNI_COMMIT"
echo "OmniMemEval at $(git -C "$OMNI" rev-parse HEAD)"

# 2. the library name, nothing else
python3 - "$OMNI/scripts/client_factory/registry.py" <<'PY'
import sys
path = sys.argv[1]
src = open(path).read()
if '"openway"' not in src:
    anchor = '    "mem9":        ("mem9_client",        "Mem9Client"),\n'
    assert anchor in src, "registry layout changed; add the name by hand"
    src = src.replace(anchor, anchor + '    "openway":     ("openway_client",     "OpenwayClient"),\n')
    open(path, "w").write(src)
PY

# 3. python environment with what steps 3-6 import
if [ ! -x "$WORK/venv/bin/python" ]; then
    python3 -m venv "$WORK/venv"
    "$WORK/venv/bin/pip" install --quiet --upgrade pip
    "$WORK/venv/bin/pip" install --quiet openai python-dotenv numpy pandas openpyxl rich tqdm tiktoken
fi
PY="$WORK/venv/bin/python"

umask 077
cat > "$ENV_FILE" <<EOF
ANSWER_MODEL=gpt-4.1-mini-2025-04-14
ANSWER_API_KEY=$OPENAI_API_KEY
ANSWER_BASE_URL=https://api.openai.com/v1
EVAL_MODEL=gpt-4o-mini-2024-07-18
EVAL_API_KEY=$OPENAI_API_KEY
EVAL_BASE_URL=https://api.openai.com/v1
EOF
umask 022

# 4. a fresh results directory: our memory blocks (and answers, for "judge")
mkdir -p "$DEST"
cp "$SRC/openway_beam_search_results.json" "$SRC/openway_beam_search_status.json" \
   "$SRC/openway_beam_ingestion_stats.json" "$DEST/"
if [ "$MODE" = "judge" ]; then
    cp "$SRC/openway_beam_responses.json" "$SRC/openway_beam_response_status.json" "$DEST/"
fi

cd "$OMNI"
export OMNIMEMEVAL_ENV_FILE="$ENV_FILE"
if [ "$MODE" = "answer" ]; then
    "$PY" scripts/beam/beam_responses.py --lib openway --version "$VERSION" --llm-workers 10 \
        --save-model-input 0 --skip-failed-answer 0
fi
"$PY" scripts/beam/beam_eval.py --lib openway --version "$VERSION" --llm-workers 10 --num_runs 1 \
    --skip-failed-judge 0
"$PY" scripts/beam/beam_metric.py --lib openway --version "$VERSION"

# 5. side by side
echo
python3 "$ROOT/verify/compare_replay.py" "$DEST" --run "$RUN"
echo
echo "replay outputs: $DEST"
