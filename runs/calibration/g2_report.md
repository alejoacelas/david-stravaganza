# G2 issue matcher: calibration report

**Verdict: calibrated, with a known lean.** On held-out papers the batch matcher agrees with expert labels on 89.7% of pairs. That is level with the LLM judges in Kim et al. (89–93%). It misses some matches that experts accept (sensitivity 81%) but rarely invents one (specificity 97%). So recall of human issues measured with G2 is a slight underestimate.

- Module: `sv/graders/g2_match.py`, prompt `g2-v1` (no prompt iterations were needed). Model: `claude-opus-5-5`, no paper text given (items only).
- Interfaces: `match(a, b)` judges one pair; `match_lists(paper_id, ai_items, reference_issues)` makes one call per paper and returns, for each reference issue, every AI item that matches.
- Definition: a match needs the same target in the paper and the same kind of flaw. The two items may give different reasons. A shared topic alone is not a match.

## Data

PeerReview Bench `similarity_check` (Kim, Neubig et al. 2026; CC-BY-4.0) has 164 expert-labelled pairs from 32 Nature-family papers: 70 similar and 94 not similar, of which 85 are AI–AI pairs and 79 are AI–human pairs. Papers were split with seed 20261110:

- dev (11 papers, 57 pairs): 1, 4, 6, 14, 17, 31, 34, 41, 62, 65, 78
- test (21 papers, 107 pairs): 18, 19, 28, 29, 32, 33, 35, 36, 37, 42, 43, 44, 51, 59, 60, 61, 63, 64, 66, 74, 77

Caveats that change how far to trust the numbers:

- The released set already excludes 74 of 238 pairs. Those were pairs where both GPT-5.4 and Gemini disagreed with the label and an audit then judged the label wrong or ambiguous. This removes the hardest cases for LLM judges, so every LLM accuracy on this set, ours included, is inflated.
- The dataset has no second human labeller on similarity, so there is no human–human ceiling. The comparison point is the paper's Table 19.

## Results

| Split | Mode | n | Accuracy [95% Wilson] | Cohen κ | Gwet AC1 | Sensitivity | Specificity |
|---|---|---|---|---|---|---|---|
| **test** | **match_lists** | 107 | **89.7% [82.5, 94.2]** | 0.79 | 0.80 | 80.9% | 96.7% |
| dev | match_lists | 57 | 96.5% [88.1, 99.0] | 0.93 | 0.93 | 95.7% | 97.1% |
| dev | match (pair) | 57 | 98.2% [90.7, 99.7] | 0.96 | 0.97 | 100% | 97.1% |

- Test accuracy by pair type: AI–AI 92.5%, AI–human 87.0%.
- Four-way relation accuracy (pair mode, dev): 71.9%. Most errors put pairs that experts called "same argument, different evidence" into "same reasoning". This has no effect on the binary label.
- Reference (Kim et al. Table 19, all 164 pairs, with the full paper text): LLM judges score 89–93% binary. Claude Opus 4.7 scores 92.7%.
- Pair mode was not run on the test split, to save budget. It has only dev numbers, so the headline is `match_lists`, the interface later stages use.

**Reinstein annotations (3 Unjournal issues, Acemoglu et al. 2024, against the GPT-5.2 Pro list):** the grader agrees on all 3.

| Issue | Reinstein's score and match | G2 output |
|---|---|---|
| H1 | 0.05, no match | no match |
| H2 | 0.85, matches L5 | L5, confidence 0.85 |
| H3 | 0.55, matches L6 | L6, confidence 0.40 |

H3 is borderline for both raters. This is a consistency check on 3 items, not a calibration.

## Known failure modes (from the 11 test errors)

- **Strict on broad matches (9 of 11 errors are missed matches).** Experts call items similar when both say "aspect X is inadequate" for different reasons, for example two different modelling-adequacy complaints, or two system-level energy-analysis gaps. G2 treats these as different criticisms. This is defensible under "same criticism", but G2 recall numbers will be conservative.
- **2 false matches.** Both are pairs on the same method where experts saw different flaw types: the extraction method alters composition versus it underestimates metal toxicity, and compound mortality assumes independence versus the comparison is mechanical. These are close calls.
- **Confidence is not calibrated.** `match_lists` can return a match with confidence below 0.5, as with H3 above. Treat the presence of a match as the label and confidence as a rough score.
- The grader was not given the paper text. Items that point to the paper only by location, such as "the result on p. 12", may be under-matched. `context=` accepts an excerpt but was not calibrated.

## Cost

$8.64 on the ledger's deliberately high rates: $3.01 pair mode, $5.55 list mode (dev and test), $0.08 Reinstein.

Rerun with `uv run python -m sv.graders.calibrate_g2 {dev|test|reinstein} [--mode pair|list|both]`. First run `uv run --with pyarrow python -m sv.graders.prep_prb`. Predictions go to `runs/calibration/preds/`, which git ignores.
