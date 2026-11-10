# Reviewer runs

Model: claude-opus-5-5, effort "high", input = paper text only, no tools. Code: `sv/reviewers/`.
Outputs: `runs/reviews/<reviewer>/<set>/<paper_id>.json`; raw replies and notes in `_meta/`.

| Reviewer | Set | Papers | Items | Per paper | By severity | Failures | Truncated |
|---|---|---|---|---|---|---|---|
| R0a | uj | 14 | 163 | 10-12 | - | 0 | 0 |
| R0b | planted | 0 | 0 | 0-0 | - | 30 | 0 |
| R0b | uj | 14 | 191 | 12-15 | - | 0 | 0 |
| R1 | planted | 14 | 137 | 8-10 | s1:28, s2:95, s3:14 | 0 | 0 |
| R1 | uj | 14 | 140 | 10-10 | s1:35, s2:89, s3:16 | 0 | 0 |
| R1s0 | planted | 14 | 137 | 8-10 | s1:28, s2:95, s3:14 | 16 | 0 |
| R1s0 | uj | 14 | 140 | 10-10 | s1:35, s2:89, s3:16 | 0 | 0 |
| R1s1 | uj | 14 | 140 | 10-10 | s1:33, s2:89, s3:18 | 0 | 0 |
| R1s2 | uj | 14 | 139 | 9-10 | s1:37, s2:85, s3:17 | 0 | 0 |
| R2 | planted | 12 | 119 | 9-10 | s1:29, s2:77, s3:13 | 18 | 0 |
| R2 | uj | 14 | 139 | 9-10 | s1:29, s2:93, s3:17 | 0 | 0 |

R1 is R1s0 under another name. R2 pools R1s0-R1s2, so its own cost is only the verifier call.

## Cost (ledger tags `rev:*`, conservative rates)

| Part | USD |
|---|---|
| R0b | 3.33 |
| R1s0 | 23.22 |
| R1s1 | 12.03 |
| R1s2 | 12.27 |
| R2verify | 12.47 |
| **Total** | **63.32** |

## Prompts

R0b: data/raw/llm-uj-research-eval/methods.qmd: chunks prompt-role (PROMPT_ROLE, PROMPT_DEBIASING) and focal-config (PROMPT_OUTPUT_WITH_ISSUES, key_issues line); user turn from chunk focal-kickoff. Kept their role, debiasing and key-issues wording; dropped the
assessment summary and metrics keys. The paper goes in the user turn as page-marked text
(they attached the PDF).

System:
```
Your role -- You are an academic expert as well as a practitioner across every relevant field -- use all your knowledge and insight. You are acting as an expert research evaluator/reviewer.


Do not look at any existing ratings or evaluations of these papers you might find on the internet or in your corpus, do not use the authors' names, status, or institutions in your judgment; ignore where (or whether) the work is published, the prestige of any venue, and how much attention it has received. Do not use this as evidence about quality. You must base all judgments entirely on the content of the PDF.


Fill the top-level key:
- `key_issues`: a numbered list (array of strings) identifying the most important methodological, interpretive, or evidential issues in the paper. Each item should be a concise statement (1-2 sentences) that a reader could use as a checklist. Aim for 5-15 issues depending on the paper. Order from most to least important.

Return STRICT JSON of the form {"key_issues": ["...", "..."]}. No preamble. No markdown. No extra text.
```
User:
```
<paper>
{paper}
</paper>

Return STRICT JSON per schema. No extra text.
```

R1 and the R2 verifier put the paper in a shared, prompt-cached system block:
```
You are an expert research evaluator. The paper under review is below, as page-marked text: "[p. N]" marks the start of PDF page N.{note}

<paper>
{paper}
</paper>
```
R1 user turn:
```
Write a critical review of the paper as a list of its most important problems.

Prefer specific, checkable problems:
- internal inconsistencies (text vs tables, between sections, between tables)
- numbers that don't add up (sums, shares, sample sizes, magnitudes, units)
- identification threats tied to specific features of this design (not generic "endogeneity may be a concern")
- claims in the abstract, introduction or conclusion that go beyond what the results support
Avoid generic asks (more robustness checks, more heterogeneity, external validity in general, more literature) unless you can name the specific check and why its absence matters here. If you find only a few real problems, list only those: say nothing rather than pad.

Severity:
 3 = would change the paper's main conclusion or its use in a decision
 2 = materially weakens a claim
 1 = minor

Each item is a JSON object:
{"claim": "the problem, stated specifically (1-3 sentences)",
 "severity": 1|2|3,
 "consequence": "how this changes the paper's conclusion or a decision based on it; quantify when possible (e.g. which estimate moves, by roughly how much, which claim no longer follows)",
 "evidence": [{"quote": "verbatim text copied from the paper", "page": N}]}

Evidence: 1-3 quotes per item. Copy each quote exactly, character for character, from the paper text provided above (a sentence or a table row fragment of up to ~40 words). Give the page number from the nearest preceding "[p. N]" marker. Do not paraphrase inside a quote, and do not quote text that is not in the provided paper.

At most 10 items, ranked by severity (highest first), then by importance.
Return only a JSON array of items. No preamble, no markdown.
```
R2 verifier user turn (items = the pooled R1s0-R1s2 items as JSON):
```
Below are candidate review items about the paper above, pooled from three independent reviews. Many are duplicates.

<items>
{items}
</items>

Check each item against the paper and decide keep or drop. Drop an item if:
- its quotes are not in the paper or do not support its claim,
- its claim misreads the paper (the paper already addresses it, or the numbers/text say otherwise),
- it is generic (could be said of most papers in the field without reading this one).
Merge items that raise the same underlying problem into one item: keep the clearest claim, the best-supported consequence and the best 1-3 quotes (quotes must stay verbatim from the paper, with page numbers from the "[p. N]" markers). Re-assess severity where needed.

Severity:
 3 = would change the paper's main conclusion or its use in a decision
 2 = materially weakens a claim
 1 = minor

Output the final list: at most 10 items, ranked by severity (highest first), then importance. Fewer is fine. Output JSON of the form:
{{"decisions": [{{"source_id": "...", "action": "keep"|"drop"|"merged", "reason": "short"}}],
 "final": [{{"claim": ..., "severity": ..., "consequence": ..., "evidence": [{{"quote": ..., "page": ...}}], "source_ids": ["..."]}}]}}
Return only the JSON. No preamble, no markdown.
```

## Planted set: incomplete

The Anthropic account ran out of credit (API 400 "credit balance is too low") during the
planted runs, which were then stopped. Done so far:
- R2 (12/30): P01-a P01-b P01-c P02-a P02-b P02-c P03-a P03-b P03-c P04-a P04-b P04-c 
- R1s0 (14/30): P01-a P01-b P01-c P02-a P02-b P02-c P03-a P03-b P03-c P04-a P04-b P04-c P05-a P05-c 
- R0b: 0/30.
Rerunning the same commands resumes from the disk cache: finished calls cost nothing.
