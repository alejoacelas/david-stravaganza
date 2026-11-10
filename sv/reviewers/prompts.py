"""Reviewer prompts. R0b copies the "Just Ask the Model" GPT-5.2 Pro focal-run wording."""

R0B_SOURCE = ("data/raw/llm-uj-research-eval/methods.qmd: chunks prompt-role (PROMPT_ROLE, "
              "PROMPT_DEBIASING) and focal-config (PROMPT_OUTPUT_WITH_ISSUES, key_issues line); "
              "user turn from chunk focal-kickoff")

# Verbatim from methods.qmd (PROMPT_ROLE, PROMPT_DEBIASING).
_ROLE = """
Your role -- You are an academic expert as well as a practitioner across every relevant field -- use all your knowledge and insight. You are acting as an expert research evaluator/reviewer.
"""
_DEBIASING = """
Do not look at any existing ratings or evaluations of these papers you might find on the internet or in your corpus, do not use the authors' names, status, or institutions in your judgment; ignore where (or whether) the work is published, the prestige of any venue, and how much attention it has received. Do not use this as evidence about quality. You must base all judgments entirely on the content of the PDF.
"""
# PROMPT_OUTPUT_WITH_ISSUES reduced to the key_issues key (wording of that line kept).
_OUTPUT = """
Fill the top-level key:
- `key_issues`: a numbered list (array of strings) identifying the most important methodological, interpretive, or evidential issues in the paper. Each item should be a concise statement (1-2 sentences) that a reader could use as a checklist. Aim for 5-15 issues depending on the paper. Order from most to least important.

Return STRICT JSON of the form {"key_issues": ["...", "..."]}. No preamble. No markdown. No extra text.
"""
R0B_SYSTEM = "\n".join([_ROLE, _DEBIASING, _OUTPUT]).strip()
# Their user turn was the PDF file followed by this line; we send the page-marked text instead.
R0B_USER = "<paper>\n{paper}\n</paper>\n\nReturn STRICT JSON per schema. No extra text."

# R1 and the R2 verifier share this system block so the paper is prompt-cached across calls.
PAPER_SYSTEM = """You are an expert research evaluator. The paper under review is below, as page-marked text: "[p. N]" marks the start of PDF page N.{note}

<paper>
{paper}
</paper>"""

_SEVERITY = """Severity:
 3 = would change the paper's main conclusion or its use in a decision
 2 = materially weakens a claim
 1 = minor"""

_ITEM_SCHEMA = """Each item is a JSON object:
{"claim": "the problem, stated specifically (1-3 sentences)",
 "severity": 1|2|3,
 "consequence": "how this changes the paper's conclusion or a decision based on it; quantify when possible (e.g. which estimate moves, by roughly how much, which claim no longer follows)",
 "evidence": [{"quote": "verbatim text copied from the paper", "page": N}]}"""

R1_USER = f"""Write a critical review of the paper as a list of its most important problems.

Prefer specific, checkable problems:
- internal inconsistencies (text vs tables, between sections, between tables)
- numbers that don't add up (sums, shares, sample sizes, magnitudes, units)
- identification threats tied to specific features of this design (not generic "endogeneity may be a concern")
- claims in the abstract, introduction or conclusion that go beyond what the results support
Avoid generic asks (more robustness checks, more heterogeneity, external validity in general, more literature) unless you can name the specific check and why its absence matters here. If you find only a few real problems, list only those: say nothing rather than pad.

{_SEVERITY}

{_ITEM_SCHEMA}

Evidence: 1-3 quotes per item. Copy each quote exactly, character for character, from the paper text provided above (a sentence or a table row fragment of up to ~40 words). Give the page number from the nearest preceding "[p. N]" marker. Do not paraphrase inside a quote, and do not quote text that is not in the provided paper.

At most 10 items, ranked by severity (highest first), then by importance.
Return only a JSON array of items. No preamble, no markdown."""

VERIFY_USER = """Below are candidate review items about the paper above, pooled from three independent reviews. Many are duplicates.

<items>
{items}
</items>

Check each item against the paper and decide keep or drop. Drop an item if:
- its quotes are not in the paper or do not support its claim,
- its claim misreads the paper (the paper already addresses it, or the numbers/text say otherwise),
- it is generic (could be said of most papers in the field without reading this one).
Merge items that raise the same underlying problem into one item: keep the clearest claim, the best-supported consequence and the best 1-3 quotes (quotes must stay verbatim from the paper, with page numbers from the "[p. N]" markers). Re-assess severity where needed.

{severity}

Output the final list: at most 10 items, ranked by severity (highest first), then importance. Fewer is fine. Output JSON of the form:
{{"decisions": [{{"source_id": "...", "action": "keep"|"drop"|"merged", "reason": "short"}}],
 "final": [{{"claim": ..., "severity": ..., "consequence": ..., "evidence": [{{"quote": ..., "page": ...}}], "source_ids": ["..."]}}]}}
Return only the JSON. No preamble, no markdown."""
VERIFY_USER = VERIFY_USER.replace("{severity}", _SEVERITY)
