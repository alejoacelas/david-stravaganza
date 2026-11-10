# Plan: grounded graders for an AI research reviewer

Goal: compare a naive one-shot reviewer with improved reviewers, scored by narrow
graders that are each calibrated against real labels before use.

## Data

- `data/papers/<id>.txt`: page-marked text of the 14 Unjournal papers with curated human
  issue lists (from the llm-uj-research-eval repo). Git-ignored.
- `data/derived/uj_gold_issues.json`: the curated human issues per paper (43 in total).
- `data/derived/uj_baseline_gpt52pro_issues.json`: the GPT-5.2 Pro key-issue lists from
  "Just Ask the Model" (the published naive baseline).
- `data/raw/`: cloned source repos (Unjournal data, llm-uj-research-eval, I4R meta paper).

## Shared item format

Every reviewer writes `runs/reviews/<reviewer>/<set>/<paper_id>.json`, a list of items:

```json
{"id": "R1-3", "claim": "...", "severity": 1-3, "consequence": "...",
 "evidence": [{"quote": "verbatim text from the paper", "page": 12}]}
```

Severity: 3 = would change the paper's main conclusion or its use in a decision,
2 = materially weakens a claim, 1 = minor. Baseline items have only `claim`.

## Narrow graders (each calibrated on real labels)

| Grader | Judges | Calibrated against | Owner |
|---|---|---|---|
| G1 evidence check | Quotes exist in the paper (fuzzy match), page right | Real quotes vs perturbed fakes | gold workstream |
| G2 issue matcher | Item raises the same issue as a reference issue | PeerReview Bench expert similarity labels; Reinstein's match annotations | calibration workstream |
| G3 item quality | Correct → significant → evidence sufficient (Kim et al. cascade) | PeerReview Bench doubly-annotated expert items | calibration workstream |
| G4 planted-error detection | Item names and locates a planted error; false alarms on clean twin | Construction (known location) | planted workstream |

A grader is used for headline numbers only if its agreement with experts is within
reach of human–human agreement on a held-out split; otherwise it is reported as
uncalibrated.

## Reviewers

- R0a: published GPT-5.2 Pro baseline lists (no new calls).
- R0b: the same one-shot prompt, run on Claude Opus 5.5 (paper text only).
- R1: structured critique: each item must carry verbatim evidence, a severity and a
  stated consequence; capped at 10 items.
- R2: R1 run three times, pooled, each item checked against the paper by a verifier
  pass, deduplicated and ranked by severity.

## Metrics (paper-clustered bootstrap CIs)

1. Recall of human issues (G2), overall and on "necessary/important" issues.
2. Item quality rate (G3) and evidence-verified rate (G1), for AI and for the human issues.
3. Planted errors: recall, location accuracy, false-alarm rate on clean twins (G4).
4. Run-to-run stability (R1 over three runs).

## Budget

Model calls go through `sv/llm.py` (cache, ledger in `runs/ledger.jsonl`, hard cap
`SV_BUDGET_USD`, default $200, at deliberately high per-token rates).

## Deferred

- Code reruns on I4R papers: no Stata on this machine, and openICPSR packages need a login.
- Disguised variants and prospective papers (contamination controls).
