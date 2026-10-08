# Data license — CC BY-SA 4.0

The contents of `data/` and `results/` are licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)
(CC BY-SA 4.0).

## Source material

`data/beam_100k.json` is the 100K scale of the **BEAM** benchmark, in the format
produced by OmniMemEval's `data/beam/prepare_beam.py`. The files in `results/`
contain BEAM's questions, reference answers and rubrics, and conversation content
from BEAM recalled in memory blocks and answers.

- **Work:** BEAM (Beyond a Million Tokens)
- **Authors:** M. Tavakoli et al.
- **Paper:** *Beyond a Million Tokens: Benchmarking and Enhancing Long-Term Memory in LLMs*, ICLR 2026, [arXiv:2510.27246](https://arxiv.org/abs/2510.27246)
- **Source:** [github.com/mohammadtavakoli78/BEAM](https://github.com/mohammadtavakoli78/BEAM), [huggingface.co/datasets/Mohammadta/BEAM](https://huggingface.co/datasets/Mohammadta/BEAM)
- **License:** CC BY-SA 4.0

## Changes

- The dataset file is reproduced unchanged from the OmniMemEval preparation script's output.
- The files in `results/` are outputs of running the benchmark: memory blocks, model answers, judge verdicts and scores. They are adaptations of BEAM and are shared under the same license.
