# Results: naive vs improved reviewers, scored by calibrated graders

Run of 10 Nov 2026. Unjournal set complete. Planted-error set incomplete: the Anthropic
account ran out of credit partway through.

## Headline

- **Recall of the human key issues didn't improve.** At equal list length (each reviewer's
  first 10 items), all four reviewers recover about half of the 43 issues curated by the
  Unjournal evaluation manager (44–51%, confidence intervals overlapping).
- **What did improve is auditability.** The structured reviewers (R1, R2) tie every
  criticism to verbatim quotes, and 709 of 710 quotes were found word for word in the
  paper. The naive reviewers give no evidence to check.
- **The item-quality grader (G3) can't yet tell the reviewers apart fairly.** It rates the
  improved reviewers' items far higher (94% fully positive for R2, 48% for the published
  GPT baseline), but it also rates the manager's own key issues only 60% fully positive.
  Most of the gap is probably presentation (quotes and stated consequences) and possibly
  Claude grading Claude, not better criticism.

## Reviewers

| Id | What it is |
|---|---|
| R0a | Published GPT-5.2 Pro key-issue lists from "Just Ask the Model" (no new calls) |
| R0b | Their one-shot key-issues prompt, run on Claude Opus 5.5 with the paper text |
| R1 | Structured critique: each item has verbatim quotes, a severity and a stated consequence; at most 10 items |
| R2 | R1 run three times, pooled, then a verifier pass that drops unsupported or generic items, merges duplicates and ranks |

## Graders and their calibration

| Grader | Calibrated against | Result on held-out data | Use |
|---|---|---|---|
| G1 quote check (code) | 600+ real and fake quotes from the 14 papers | Precision 0.996, recall 0.93 | Reliable |
| G2 issue matcher | PeerReview Bench expert similarity labels; Reinstein's 3 matches | 89.7% agreement (AC1 0.80); sensitivity 81%, specificity 97% | Reliable; recall is understated by roughly a fifth |
| G3 item quality | PeerReview Bench, 540 doubly-annotated items | Correctness 81% vs experts' 86% with each other; significance and evidence at human level | Calibrated on Nature papers; fails the sanity check below on Unjournal text |
| G4 planted-error scorer | 24 hand-made cases | 24/24, all easy | Not yet tested on real reviewer output |

## Unjournal set (14 papers)

Recall uses G2. Brackets are 95% confidence intervals from resampling papers.

| Reviewer | Items per paper | Curated-issue recall, first 10 items | Curated-issue recall, all items | Evaluator-criticism recall, all items | G3 fully positive | Quotes found |
|---|---|---|---|---|---|---|
| R0a GPT-5.2 Pro baseline | 11.6 | 0.51 [0.39, 0.67] | 0.54 [0.41, 0.70] | 0.26 [0.19, 0.34] | 0.48 [0.38, 0.59] | no quotes |
| R0b Opus 5.5 one-shot | 13.6 | 0.49 [0.36, 0.63] | 0.63 [0.48, 0.82] | 0.36 [0.29, 0.45] | 0.81 [0.74, 0.87] | no quotes |
| R1 structured | 10.0 | 0.44 [0.28, 0.64] | 0.44 [0.28, 0.64] | 0.17 [0.12, 0.24] | 0.86 [0.81, 0.92] | 333/334 |
| R2 pooled + verified | 9.9 | 0.51 [0.36, 0.67] | 0.51 [0.36, 0.67] | 0.21 [0.15, 0.28] | 0.94 [0.86, 1.00] | 376/376 |
| Human evaluator criticisms (sample of 12 per paper) | – | – | – | – | 0.21 [0.16, 0.27] | – |

- "Curated issues" are the 43 key issues the evaluation manager wrote up. "Evaluator
  criticisms" are 434 individual criticisms extracted from the full evaluator reports.
- "Fully positive" means G3 judged the item correct, significant and backed by sufficient
  evidence (the Kim et al. standard).
- The published study reported 80% recall for R0a with its own LLM matcher. Ours finds 54%
  with a stricter, calibrated matcher.
- R0b's higher all-items recall comes from listing more items. At 10 items it matches R0a.
- Stability: 81% of R1's seed-1 items match an item from seed 0. The seed-2 comparison
  didn't run (no credit).

### Why G3's quality numbers aren't headline evidence yet

- G3 rated the manager's 43 curated key issues: 36 correct, 30 significant, 26 fully
  positive (60%). All 7 issues marked "necessary" were rated significant. These issues
  are the papers' key problems by construction, so 60% is a floor on how far G3
  underrates human-written criticisms on this data.
- Human items carry no paper quotes (their support is the evaluator's prose), so they
  fail "evidence sufficient" more often. The AI items from R1 and R2 are written to pass
  exactly that check.
- G3 runs on Claude Opus 5.5, the same model as R0b, R1 and R2. Self-preference could
  explain part of the gap between R0b (81%) and the GPT baseline R0a (48%).
- G3 almost never uses "not significant", so significance rates run high for everyone.

## Planted-error set

Built: 10 papers not in the Unjournal set, each with a clean copy and two copies carrying
one planted error (20 variants, six error types). Reviewer outputs exist only for papers
P01–P04 (R1 and R2) and P05 (R1 only); R0b has none. Nothing has been scored. This is the
test that can show whether the improved reviewers find real errors and avoid false
alarms, so it's the main gap.

## Spend

The ledger shows $178, but entries before the rate fix were logged at about four times
Opus 5.5's reported price. At reported rates the uncached input and output come to
about $57, plus prompt-cache writes; the account's credit ran out at that point.

## What it would take to finish

1. Add API credit (roughly $30–40 at reported rates should cover the rest).
2. Rerun the planted set: `uv run python -m sv.reviewers.run --reviewer R0b --set planted`,
   then R1 and R2 the same way. Finished calls come back from the cache at no cost.
3. Score it: `uv run python -m sv.score planted R0b R1 R2`, and spot-check G4 on a few
   real detections.
4. Fix G3 before trusting quality numbers: calibrate it on Unjournal-style items, for
   example by requiring that the manager's "necessary" and most "optional but important"
   issues come out significant, and grade with a non-Claude model to rule out
   self-preference.

## Files

- Plan: `docs/plan.md`
- Calibration reports: `runs/calibration/g2_report.md`, `runs/calibration/g3_report.md`,
  `runs/gold/report.md`
- Reviewer prompts and counts: `runs/reviews_report.md`
- Numbers: `runs/results/uj_summary.json`, `runs/results/uj_analysis.json`,
  `runs/results/uj_per_paper.json`
