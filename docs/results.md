# Results: naive vs improved reviewers, scored by calibrated graders

Run of 10 Nov 2026. The Unjournal set is complete, with 13 usable papers. The
planted-error set is incomplete because the Anthropic account ran out of credit.

## Headline

- **Recall of the human key issues didn't improve.** At equal list length (each
  reviewer's first 10 items), the published GPT baseline and the pooled reviewer R2 each
  recover 55% of the evaluation manager's 40 usable key issues. R1 recovers 48%. Across
  the evaluators' 400-odd individual criticisms, R2 recovers fewer than the one-shot
  Opus run R0b (21% vs 28%), although both use the same model.
- **What did improve is auditability and specificity.** R1 and R2 tie every criticism to
  verbatim quotes, and 709 of 710 quotes were found word for word in the paper. Reading
  two papers' lists side by side, R2's items are more specific than the baseline's: they
  name exact numbers and tables, where the baseline raises generic concerns. Both lists
  share the same core issues.
- **The item-quality grader (G3) can't yet rank the reviewers fairly.** It rates 94% of
  R2's items fully positive and 50% of the GPT baseline's. Three things make that gap
  unreliable:
  - G3 rated only 26 of the manager's 41 key issues (63%) fully positive.
  - Its inputs aren't blind: the formats differ by source.
  - It's the same model as R0b, R1 and R2.

## Data errors found (inherited from the source study)

- **Benabou et al. 2023:** the PDF in the study's repository is a different paper ("Ends
  versus Means", NBER w32073) from the one evaluated ("Willful Ignorance and Moral
  Behavior"). The published baseline was run on the wrong paper. Excluded.
- **Peterman et al. 2025:** its one curated issue describes the Weaver paper. Excluded
  from curated recall.

Both are worth telling the "Just Ask the Model" team.

## Reviewers

| Id | What it is |
|---|---|
| R0a | Published GPT-5.2 Pro key-issue lists from "Just Ask the Model" (PDF input; no new calls) |
| R0b | Their one-shot key-issues prompt on Claude Opus 5.5, with paper text as input. It drops their 1,000-word summary step. |
| R1 | Structured critique: every item has verbatim quotes, a severity and a stated consequence; at most 10 items |
| R2 | R1 run three times, pooled, then a verifier pass that drops unsupported or generic items, merges duplicates and ranks |

## Graders and their calibration

| Grader | Calibrated against | Result on held-out data | Use |
|---|---|---|---|
| G1 quote check (code) | 600+ real and fake quotes from the 14 papers | Precision 0.996, recall 0.93 | Reliable |
| G2 issue matcher | PeerReview Bench expert similarity labels; Reinstein's 3 matches | 89.7% agreement (AC1 0.80); sensitivity 81%, specificity 97% | Reliable; it misses about a fifth of true matches, so recall is understated |
| G3 item quality | 540 doubly-annotated PeerReview Bench items | Correctness 81% vs 86% expert–expert; significance and evidence at human level | Calibrated on Nature papers only; fails the check on Unjournal text below |
| G4 planted-error scorer | 24 hand-made cases | 24/24, all easy | Not yet tested on real reviewer output |

## Unjournal set (13 papers)

Recall uses G2. Brackets are 95% confidence intervals from resampling papers.

| Reviewer | Items per paper | Key-issue recall, first 10 items | Key-issue recall, all items | Evaluator-criticism recall, first 10 | G3 fully positive | Quotes found |
|---|---|---|---|---|---|---|
| R0a GPT-5.2 Pro baseline | 11.6 | 0.55 [0.42, 0.74] | 0.58 [0.45, 0.77] | 0.22 [0.16, 0.29] | 0.50 [0.40, 0.60] | no quotes |
| R0b Opus 5.5 one-shot | 13.6 | 0.53 [0.40, 0.68] | 0.68 [0.53, 0.90] | 0.28 [0.21, 0.36] | 0.81 [0.74, 0.88] | no quotes |
| R1 structured | 10.0 | 0.48 [0.30, 0.71] | 0.48 [0.30, 0.71] | 0.18 [0.12, 0.25] | 0.85 [0.79, 0.91] | 333/334 |
| R2 pooled + verified | 9.9 | 0.55 [0.40, 0.74] | 0.55 [0.40, 0.74] | 0.21 [0.16, 0.28] | 0.94 [0.85, 1.00] | 376/376 |
| Human evaluator criticisms (12 sampled per paper) | – | – | – | – | 0.22 [0.17, 0.28] | – |

- "Key issues" are the 40 issues the evaluation manager curated. "Evaluator criticisms"
  are the individual criticisms extracted from the full evaluator reports.
- "Fully positive" means G3 judged an item correct, significant and backed by sufficient
  evidence, the Kim et al. standard.
- The published study reported 80% recall for R0a. That counted partial matches over a
  70-issue split of the same material, so it isn't comparable to these numbers.
- R0b's higher all-items recall comes from listing more items. Most of its lead on
  evaluator criticisms comes from three papers: Clancy, Frech and McGuire. R1 recovered
  only 2 of McGuire's 57 evaluator criticisms.
- Stability: 82% of R1's seed-1 items match an item from seed 0. The seed-2 comparison
  didn't run because the credit ran out.

### Why the G3 numbers aren't headline evidence yet

- **It underrates human key issues.** G3 rated the manager's 41 key issues on the
  included papers: 36 correct, 30 significant, 26 fully positive. All 7 issues marked
  "necessary" came out significant. These issues are the papers' key problems by
  construction, so G3 underrates criticisms written in human style.
- **Its inputs show where each item came from.** Human items read "From the evaluator's
  report". R0a and R0b items read "(no quotes given)". R1 and R2 items carry quote and
  consequence lines, which is what the evidence check rewards.
- **Human items mostly fail on correctness.** 46 of 164 were rated incorrect. Some of
  those rejections suggest the evaluators read an earlier version of the paper; I haven't
  checked this.
- **R0a's low score is mostly the evidence dimension.** 60 of its 156 correct items were
  rated "evidence insufficient", against 12 of 180 for R0b. The rest of the R0a–R0b gap
  could be self-preference, since Claude grades Claude, or differences in input and
  prompt.
- **G3 almost never says "not significant"** (once in 795 grades), so significance runs
  high for everyone.

## Planted-error set

- **Built:** 10 papers outside the Unjournal set. Each has a clean copy and two copies
  with one planted error: 20 variants covering six error types.
- **Reviewer outputs:**
  - P01–P04: R1 and R2.
  - P05: R1 only.
  - R0b: none.
- **Scored:** nothing yet.

This is the test that can show whether the improved reviewers find real errors and
avoid false alarms, so it's the main gap.

## Spend

The ledger shows $178, but entries made before the rate fix were logged at about four
times Opus 5.5's reported price. The real total is around $73: uncached input and output
come to $57 at reported rates, and prompt-cache writes add the rest. The account's credit
ran out at that point.

## What it would take to finish

1. Add API credit. About $30–40 at reported rates should cover the rest.
2. Rerun the planted set: `uv run python -m sv.reviewers.run --reviewer R0b --set planted`,
   then the same for R1 and R2. Calls that already finished come from the cache at no cost.
3. Score it with `uv run python -m sv.score planted R0b R1 R2`, then spot-check G4 on a
   few real detections.
4. Fix G3 before trusting its quality numbers:
   - Render all sources in one neutral format.
   - Calibrate it on Unjournal-style items, for example by requiring the manager's key
     issues to come out significant.
   - Grade with a non-Claude model, to rule out self-preference.

## Files

- Plan: `docs/plan.md`
- Calibration reports: `runs/calibration/g2_report.md`, `runs/calibration/g3_report.md`,
  `runs/gold/report.md`
- Reviewer prompts and counts: `runs/reviews_report.md`
- Numbers: `runs/results/uj_analysis.json` (13-paper figures above),
  `runs/results/uj_summary.json` and `uj_per_paper.json` (all 14 papers, before
  exclusions)
