"""G3 item-quality grader: Kim et al. (2026) cascade, judged against the paper text.

For each review item: correct (bool) -> significance ("significant" | "marginal" | "not",
only if correct) -> evidence_sufficient (bool, only if correct and at least marginal).
All items of one paper go in as few calls as possible (paper text is the cached system
prompt; items are chunked). Calibrated in runs/calibration/g3_report.md.

    grade(paper_text, items) -> [{"correct", "significance", "evidence_sufficient", "rationale"}]

Items are dicts with either "text" (free-form review prose) or the shared schema
("claim", optional "evidence": [{"quote", "page"}], optional "consequence").
"""
import json
from concurrent.futures import ThreadPoolExecutor
from sv import llm

VERSION = "g3-v1"

INSTRUCTIONS = """You are an expert meta-reviewer. You will judge individual review items (criticisms written by reviewers of the research paper below) on three dimensions, applied as a cascade. Judge every item against the paper itself, as a careful domain expert who has the paper open would. Judge each item on its own merits; do not let your verdict on one item carry over to similar items.

(1) CORRECT — is the main point of the criticism correct and clearly stated?
Correct if the core factual claim holds up when checked against the paper AND a reader can tell what criticism is being made.
- Be strict on substance: if the core claim is factually wrong about the paper (says the authors did X when they did Y; says something is missing that is adequately present; criticises a choice the paper explicitly justifies for its stated goal or scope; rests on a wrong general premise), it is Not Correct, even if it sounds plausible.
- Be lenient on expression: imprecise wording, a wrong page/table/equation number, or a slightly-off peripheral detail does not make an item incorrect if the main point is right.
- If information is only partly present and the broader concern (inadequate coverage) still holds, it can be Correct.
- Too vague to tell what is being criticised → Not Correct.
- Subjective reading-experience claims ("this section is hard to follow") are Correct unless the text is plainly clear.

(2) SIGNIFICANCE — only for Correct items. Does the criticism touch a significant aspect of the paper, such that addressing it would make the paper meaningfully better?
- "significant": addressing it would make the paper substantively stronger: concerns about design, identification or methodology; missing analyses, robustness checks, comparisons or controls; unclear writing in key sections; missing context from related work; reproducibility (missing data, code or specification details); internal inconsistencies; anything that would make the argument more convincing. Do not set a high bar: the issue need not threaten the paper's validity, only be constructive and genuinely helpful.
- "marginal": worth keeping in a review but not helpful for improving the paper's substance: typos, grammar, style preferences, formatting nits that do not affect understanding, nice-to-have references that do not change the story, venue suggestions.
- "not": so minor that the review would be better without it.
Judge the underlying issue, not the reviewer's tone.

(3) EVIDENCE SUFFICIENT — only for Correct items rated significant or marginal. Does the reviewer give enough justification that a meta-reviewer could verify the criticism against the paper without substantial extra work?
Valid evidence: pointing at specific material (a quote, number, table, figure, equation, section); pointing at something specific that is absent; a specific, checkable appeal to external knowledge (a named paper, a recognised standard or method); a logical derivation from the paper's stated premises; an internal inconsistency between identified parts of the paper.
- true ("sufficient"): the evidence chain covers the core claim; a meta-reviewer could decide whether it holds without guessing at the reviewer's reasoning.
- false ("requires more"): at least one core step is unsupported ("the baselines seem weak" with none named; "this has been done before" with no reference; "results seem unlikely" with nothing specific; pointing to a gap that is actually filled).
Short but precise evidence is sufficient. Length is not evidence.

Output: a JSON array, one object per item, in the order given:
{"id": "<item id>", "correct": true|false, "significance": "significant"|"marginal"|"not"|null, "evidence_sufficient": true|false|null, "rationale": "<at most 30 words: the decisive reason>"}
Use null where the cascade stops (significance null if not correct; evidence_sufficient null if not correct or significance is "not"). Output only the JSON array."""


def render_item(it: dict) -> str:
    if it.get("text") is not None:
        return it["text"].strip() or "(empty item)"
    parts = [it.get("claim", "").strip()]
    ev = it.get("evidence") or []
    if ev:
        parts += [f'Quote{" (p. %s)" % e["page"] if e.get("page") else ""}: "{e["quote"]}"' for e in ev]
    else:
        parts.append("(no quotes given)")
    if it.get("consequence"):
        parts.append("Consequence: " + it["consequence"].strip())
    return "\n".join(parts)


def _chunks(texts, max_items=12, max_chars=30000):
    cur, size = [], 0
    for i, t in enumerate(texts):
        if cur and (len(cur) >= max_items or size + len(t) > max_chars):
            yield cur; cur, size = [], 0
        cur.append(i); size += len(t)
    if cur:
        yield cur


def _norm(o: dict) -> dict:
    c = bool(o.get("correct"))
    s = o.get("significance") if c else None
    s = {"marginally significant": "marginal", "not significant": "not"}.get(str(s).lower(), s) if s else None
    e = o.get("evidence_sufficient") if c and s in ("significant", "marginal") else None
    return {"correct": c, "significance": s, "evidence_sufficient": e, "rationale": o.get("rationale", "")}


def grade(paper_text: str, items: list[dict], *, model: str = llm.OPUS, tag: str = "g3", workers: int = 4) -> list[dict]:
    texts = [render_item(it) for it in items]
    system = INSTRUCTIONS + "\n\n=== PAPER ===\n" + paper_text
    chunks = list(_chunks(texts))

    def run(idx):
        body = "\n\n".join(f"### Item I{i + 1}\n{texts[i]}" for i in idx)
        prompt = f"Judge these {len(idx)} review items.\n\n{body}\n\nReturn the JSON array with ids {', '.join(f'I{i + 1}' for i in idx)}."
        for attempt in range(3):  # a reply can come back empty or truncated; retry with a fresh cache key
            try:
                out = llm.parse_json(llm.call(prompt, system=system, model=model, max_tokens=4000, tag=tag, seed=attempt))
            except ValueError:
                continue
            got = {o.get("id"): o for o in out if isinstance(o, dict)}
            if all(f"I{i + 1}" in got for i in idx):
                return {i: _norm(got[f"I{i + 1}"]) for i in idx}
        raise ValueError(f"grader reply missing items {idx}")

    res = run(chunks[0])  # first call writes the paper into the prompt cache
    with ThreadPoolExecutor(workers) as ex:
        for r in ex.map(run, chunks[1:]):
            res.update(r)
    return [res[i] for i in range(len(items))]
