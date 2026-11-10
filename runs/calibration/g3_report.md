# G3 item-quality grader: calibration report

**Verdict: calibrated for significance and evidence sufficiency. Correctness is near human level but stricter than experts.** On 18 held-out papers (540 items), the grader agrees with each expert about as often as the two experts agree with each other on significance and evidence. On correctness it is about 5 points below human–human agreement (paper-clustered bootstrap 95% CI for the gap: −10.1 to +0.3). It wrongly rejects some items that both experts accepted. Use correctness rates as a slightly conservative lower bound, and report AI items and human items with the same grader so the bias cancels in comparisons.

- Module: `sv/graders/g3_quality.py`, prompt `g3-v1`. Model: `claude-opus-5-5`.
- Interface: `grade(paper_text, items)` returns, for each item, `{correct, significance, evidence_sufficient, rationale}`. It judges the Kim et al. cascade: correct, then significance (significant, marginal or not), then evidence sufficient. Significance is judged only for correct items, and evidence only for items rated at least marginal.
- The paper text is the cached system prompt. Items are batched about 12 per call, and all items of a paper share the cache.
- The prompt is a domain-general rewrite of the Kim et al. annotation definitions. It has no field-specific examples, and it names identification and robustness among its examples so it applies to economics papers.

## Data

PeerReview Bench `meta_reviewer`: 908 items from 27 Nature-family papers, each labelled by two domain experts (568 human-written items, 340 AI-written items). The dataset includes the manuscript markdown, which the grader saw. It did not see figures or code; Kim et al.'s agent meta-reviewer could open them.

Our metric code reproduces the paper's human–human Table 2 on all 908 items exactly:

| Dimension | Agreement | κ | AC1 |
|---|---|---|---|
| Correctness | 85.8% | 0.28 | 0.82 |
| Significance | 59.9% | 0.31 | 0.44 |
| Evidence | 88.0% | 0.12 | 0.86 |

Papers were split with seed 20261110:

- dev (9 papers): 6, 12, 14, 15, 27, 52, 61, 79, 84
- test (18 papers): 31, 33, 34, 35, 37, 49, 50, 51, 59, 60, 62, 67, 77, 78, 80, 81, 82, 83

Paper 79 (chemical synthesis of inhibitors) is excluded. The API returns a refusal for it. It was in dev, so test is unaffected.

## Held-out results (test, 540 items, 18 papers)

P is the primary annotator, S the secondary, M the grader. Each comparison uses the items where both raters reached that stage of the cascade.

| Dimension | Pair | n | Agreement | Cohen κ | Gwet AC1 |
|---|---|---|---|---|---|
| Correctness | P–S (human ceiling) | 540 | 86.3% | 0.32 | 0.83 |
| | M–P | 540 | 82.0% | 0.11 | 0.77 |
| | M–S | 540 | 80.6% | 0.13 | 0.75 |
| Significance (3-way) | P–S | 442 | 57.0% | 0.28 | 0.39 |
| | M–P | 430 | 55.3% | 0.22 | 0.38 |
| | M–S | 418 | 59.8% | 0.20 | 0.46 |
| Evidence sufficient | P–S | 337 | 89.9% | 0.14 | 0.89 |
| | M–P | 344 | 87.2% | 0.24 | 0.85 |
| | M–S | 371 | 89.2% | 0.05 | 0.88 |

The gap is the grader's mean agreement with the two experts minus their agreement with each other, with a paper-clustered bootstrap 95% CI:

| Dimension | Gap | 95% CI |
|---|---|---|
| Correctness | −5.0 pts | [−10.1, +0.3] |
| Significance | +0.6 pts | [−12.5, +11.0] |
| Evidence | −1.7 pts | [−5.7, +2.2] |

Kim et al.'s protocol scores accuracy against the primary annotator, only on items where both experts agree up to that stage. On that protocol the grader scores:

| Dimension | Ours | Kim et al., Claude Opus 4.7 agent, all 27 papers |
|---|---|---|
| Correctness | 86.3% (n=466) | 87.9% |
| Significance | 59.1% (n=252) | 56.7% |
| Evidence | 80.3% (n=203) | 85.6% |

Results by item type on test, grader agreement with P and with S against P–S:

| Items | Dimension | M–P | M–S | P–S |
|---|---|---|---|---|
| Human-written | Correctness | 83.2% | 81.3% | 84.8% |
| | Significance | 55.2% | 58.4% | 58.2% |
| | Evidence | 81.4% | 84.0% | 85.9% |
| AI-written | Correctness | 80.4% | 79.5% | 88.4% |
| | Significance | 55.6% | 61.9% | 55.3% |
| | Evidence | 95.7% | 96.2% | 95.2% |

The correctness gap is concentrated on AI-written items, which is the use we care about.

## Prompt development (dev only, 343 items in 8 papers)

| Version | Correctness M–P / M–S (P–S) | Significance M–P / M–S (P–S) | Evidence M–P / M–S (P–S) |
|---|---|---|---|
| v1 | 82.5 / 86.3 (84.5) | 53.5 / 62.3 (63.3) | 85.5 / 91.0 (84.8) |
| v2 | 81.9 / 86.3 | 48.0 / 55.0 | 82.1 / 87.9 |

v2 redefined "not significant" to cover typos and cosmetic nits, because v1 almost never used that label. v2 was worse, so v1 went to test unchanged.

Claude Haiku 5.5 with v1 on the same 283 dev items scored 81.3 / 80.2 on correctness, against 86.2 / 85.2 for Opus. It also failed to return complete lists for 2 papers. Haiku does not match Opus, so it should not replace Opus here.

## Known failure modes (from inspecting test disagreements)

- **Too strict on correctness (48 test items both experts called correct, 27 human-written and 21 AI-written).** The grader:
  - marks questions and requests for information as Not Correct ("Did the authors use fastFVA?");
  - marks items Not Correct when they overstate a real point ("severe data leakage", "fundamental flaw");
  - rejects "missing X" items when the paper partly covers X, where experts still credit the broader concern;
  - rejects wording complaints it considers debatable.
- **Almost never uses "not significant".** Test counts: grader 2, P 97, S 56. It puts those items in marginal or significant. It rates more items significant than either expert (317, against 235 and 270). Significance rates from G3 are therefore inflated relative to experts. Comparisons between reviewers are still meaningful.
- **Version mismatch.** Some human reviews in PeerReview Bench quote text that is absent from the released manuscript (paper 12 in dev). The grader rightly reports the quote as absent, but one expert still marked the item correct. This is an artefact of the dataset. Our own reviewers read the same text the grader sees.
- **Anchoring risk.** Items from one paper share a call (Kim et al. F.3.8 report anchoring with shared context). The prompt asks for independent judgments. We did not test per-item calls.
- **Refusals.** The API refused one chemistry paper. `grade()` then raises `ValueError` after three attempts. We do not expect this on economics papers, but it is not tested.

## Cost

$59.28 on the ledger's deliberately high rates:

- v1, Opus, dev and test: $44.90. About $13 of this was a dev rerun after a `max_tokens` change altered the cache keys.
- v2, Opus, dev: $13.13
- v1, Haiku, dev: $1.22

A fresh Opus pass over the 540 test items costs about $20, so grading one paper's items costs roughly $1.

Rerun with `uv run python -m sv.graders.calibrate_g3 {dev|test} [--model M]`. Predictions go to `runs/calibration/preds/`, which git ignores. Held-out tables are in `runs/calibration/g3_test_tables.json`.
