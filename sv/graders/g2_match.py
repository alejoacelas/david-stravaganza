"""G2 issue matcher: does a review item raise the same underlying criticism as a reference issue?

"Same" means same target in the paper AND same kind of flaw asserted about it; the
reasons given may differ. Topical overlap alone is not a match. Calibrated in
runs/calibration/g2_report.md (PeerReview Bench similarity labels + Reinstein's matches).

    match(item_a, item_b, context=None) -> {"match", "confidence", "relation", "rationale"}
    match_lists(paper_id, ai_items, reference_issues, context=None)
        -> {ref_id: [{"ai_id", "confidence", "relation"}]}   # every AI item judged a match

Items are strings or dicts with "id" plus "text" or "claim" (shared schema).
"""
from sv import llm

VERSION = "g2-v1"

RELATIONS = {
    "same_issue_same_reasoning": True,       # near-paraphrase
    "same_issue_different_reasoning": True,  # same flaw about same target, different support
    "same_target_different_criticism": False,
    "different_target": False,
}

DEFINITION = """Two review items raise the SAME ISSUE when both of these hold:
1. Same target: they point at the same part or element of the paper (a specific table, figure, estimate, claim, dataset, method step, assumption, or a broader aspect such as "the identification strategy" or "the external validity of the results"). One may be more specific than the other.
2. Same criticism: once you strip out each item's specific reasons, quotes and examples and reduce it to "X is <flaw>" (wrong, missing, unjustified, biased, overstated, not robust, not generalisable, unclear, inconsistent, non-reproducible, ...), both assert the same kind of flaw about X. Different reasons for the same flaw still count as the same criticism.
Not the same issue: items about different parts of the paper; or items about the same part that assert different kinds of flaw (e.g. "Table 2 omits standard errors" vs "Table 2's sample is selected on the outcome"). Shared topic or shared vocabulary alone is never enough.
If one item bundles several criticisms, it matches the other when one of its main criticisms is the same issue as the other's main criticism.

Relations (pick one):
- same_issue_same_reasoning: same issue, and the core reasoning or evidence overlaps
- same_issue_different_reasoning: same issue, reached through substantively different reasoning or evidence
- same_target_different_criticism: same target, different kind of flaw
- different_target: different parts of the paper"""

PAIR_SYSTEM = f"""You judge whether two peer-review items about the same research paper raise the same underlying issue.

{DEFINITION}

Reason briefly (at most 80 words), then output one JSON object:
{{"relation": "<one of the four relations>", "confidence": <probability 0-1 that an expert would call these the same issue>, "rationale": "<one sentence>"}}"""

LIST_SYSTEM = f"""You match a list of AI review items against a list of reference issues raised by other reviewers of the same research paper.

{DEFINITION}

For EVERY reference issue, list every AI item that raises the same issue (same_issue_same_reasoning or same_issue_different_reasoning). An AI item may match several reference issues; a reference issue may match none. Also list, separately, AI items that share the target but make a different criticism (near misses). Judge each pair on its own; do not stretch to find a match.

Output only a JSON object:
{{"<reference id>": {{"matches": [{{"ai_id": "...", "relation": "...", "confidence": <0-1>}}], "near_misses": ["<ai id>", ...], "rationale": "<one sentence>"}}, ...}}
with one key for every reference issue id."""


def _text(it) -> str:
    if isinstance(it, str):
        return it.strip()
    return (it.get("text") or it.get("claim") or "").strip()


def _ctx(context):
    return f"=== PAPER CONTEXT ===\n{context}\n\n" if context else ""


def match(item_a, item_b, context: str | None = None, *, model: str = llm.OPUS, tag: str = "g2") -> dict:
    prompt = f"{_ctx(context)}### Item A\n{_text(item_a)}\n\n### Item B\n{_text(item_b)}\n\nDo A and B raise the same issue?"
    for seed in range(2):
        try:
            o = llm.parse_json(llm.call(prompt, system=PAIR_SYSTEM, model=model, max_tokens=1500, tag=tag, seed=seed))
            rel = o["relation"]
            if rel in RELATIONS:
                return {"match": RELATIONS[rel], "confidence": float(o.get("confidence", 0.5)),
                        "relation": rel, "rationale": o.get("rationale", "")}
        except (ValueError, KeyError):
            pass
    raise ValueError("G2 pair reply unparseable")


def match_lists(paper_id, ai_items, reference_issues, context: str | None = None, *,
                model: str = llm.OPUS, tag: str = "g2-list") -> dict:
    def ids(xs, p):
        return [(x.get("id") if isinstance(x, dict) and x.get("id") else f"{p}{i + 1}", _text(x)) for i, x in enumerate(xs)]
    ai, ref = ids(ai_items, "A"), ids(reference_issues, "R")
    prompt = (f"Paper: {paper_id}\n\n{_ctx(context)}=== REFERENCE ISSUES ===\n"
              + "\n\n".join(f"[{i}] {t}" for i, t in ref)
              + "\n\n=== AI ITEMS ===\n" + "\n\n".join(f"[{i}] {t}" for i, t in ai)
              + f"\n\nReturn the JSON object with keys: {', '.join(i for i, _ in ref)}.")
    ai_ids = {i for i, _ in ai}
    for seed in range(2):
        o = llm.parse_json(llm.call(prompt, system=LIST_SYSTEM, model=model, max_tokens=8000, tag=tag, seed=seed))
        if all(r in o for r, _ in ref):
            return {r: [m for m in o[r].get("matches", []) if m.get("ai_id") in ai_ids and RELATIONS.get(m.get("relation"), True)]
                    for r, _ in ref}
    raise ValueError("G2 list reply missing reference ids")
