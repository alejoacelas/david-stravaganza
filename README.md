# david-stravaganza

Compares a naive one-shot AI paper reviewer with improved reviewers on Unjournal papers, scored by narrow graders calibrated against human labels. Method in [docs/plan.md](docs/plan.md), findings in [docs/results.md](docs/results.md).

Run with `uv`, with `ANTHROPIC_API_KEY` in `.env`:

```sh
uv run python -m sv.prep_unjournal   # needs llm-uj-research-eval cloned into data/raw/
uv run python -m sv.reviewers.run --reviewer R1 --set uj
uv run python -m sv.score uj R0b R1 R2
```
