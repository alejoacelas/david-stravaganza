"""G4: planted-error detection grader.

For a planted variant, an item detects the planted error when it names the right
problem (an Opus judge compares the item with the manifest's description) at the
right place (one of its evidence quotes overlaps the planted span, or the judge sees
that the claim explicitly refers to the planted statement). Location accuracy is
reported separately: `located` means some item quotes the planted span at all.

For a clean twin, a false alarm is an item asserting that one of its twins' planted
errors is present in the clean text (a hallucinated version of the same error).

Usage from code:  score_variant(variant_id, items) -> dict
CLI:              uv run python -m sv.planted.g4_score runs/reviews/<reviewer>/planted
                  (scores every <variant_id>.json in that folder, writes runs/grades/g4/<reviewer>.json)
"""
import json, re, sys
from pathlib import Path
from sv import llm

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "data/planted/manifest.json"
RUN_LEN = 5  # contiguous words shared with the planted span that count as quoting it

_LIG = {"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff", "ﬃ": "ffi", "ﬄ": "ffl", "−": "-", "–": "-", "—": "-", "’": "'", "“": '"', "”": '"'}

def words(s: str) -> list[str]:
    for k, v in _LIG.items():
        s = s.replace(k, v)
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)  # undo end-of-line hyphenation
    return re.findall(r"[a-z0-9]+(?:[.,][0-9]+)*%?", s.lower())

def quote_hits(quote: str, span: str, changed: set[str]) -> bool:
    """True if the quote shares a RUN_LEN-word run with the span, or is a shorter piece of it containing a changed word."""
    q, s = words(quote), words(span)
    if not q:
        return False
    grams = {tuple(s[i:i + RUN_LEN]) for i in range(len(s) - RUN_LEN + 1)}
    if any(tuple(q[i:i + RUN_LEN]) in grams for i in range(len(q) - RUN_LEN + 1)):
        return True
    joined_q, joined_s = " ".join(q), " ".join(s)
    return len(q) < RUN_LEN and joined_q in joined_s and bool(set(q) & changed)

def changed_words(e: dict) -> set[str]:
    return set(words(e["planted_span"])) - set(words(e["original_span"]))

def load_manifest() -> dict:
    return {m["variant_id"]: m for m in json.load(open(MANIFEST))}

def _item_text(it: dict) -> str:
    ev = "; ".join(f'p.{q.get("page")}: "{q.get("quote", "")}"' for q in it.get("evidence", []) or [])
    return f'[{it.get("id")}] claim: {it.get("claim", "")}\n  consequence: {it.get("consequence", "")}\n  evidence: {ev or "(none)"}'

JUDGE_PLANTED = """You grade whether a reviewer's items found a specific error that was deliberately planted in a paper.

Planted error (type: {type}, page {page}):
- The paper originally said: "{original}"
- The planted version says: "{planted}"
- A correct detection must say: {detection}

Reviewer items:
{items}

For EACH item decide:
- nature: does the item identify this same problem (same kind of mistake about the same quantity or claim, e.g. "text says X but the table says Y", "this sentence over-claims causality")? A vague or generic concern about the same result is NOT enough; the item must say what is wrong in a way that matches the detection criterion. Credit an item even if it gets minor details (exact table number) wrong.
- location: does the item clearly point at the planted statement (quotes it, paraphrases it, or names the specific number/sentence it contains)?

Return JSON only: {{"items": [{{"id": "...", "nature": true/false, "location": true/false, "reason": "<= 20 words"}}]}}"""

JUDGE_CLEAN = """You check a reviewer's items on the CORRECT version of a paper for hallucinated errors.

In a different copy of this paper, errors were planted. The copy reviewed here is unmodified, so these errors are NOT present:
{errors}

Reviewer items:
{items}

For EACH item and each error above, decide whether the item confidently asserts that this error is present in the paper
(the same mistake about the same statement, e.g. it claims the text says the planted value, or that the sentence makes the
planted over-claim). Raising a different concern about the same passage, or a hedged question, does not count.

Return JSON only: {{"items": [{{"id": "...", "asserts_error": "<error number or null>", "reason": "<= 20 words"}}]}}"""

def _judge(prompt: str, tag: str) -> dict:
    out = llm.parse_json(llm.call(prompt, model=llm.OPUS, max_tokens=3000, tag=tag))
    return {str(x["id"]): x for x in out["items"]}

def score_variant(variant_id: str, items: list[dict], manifest: dict | None = None, tag: str = "g4") -> dict:
    man = manifest or load_manifest()
    m = man[variant_id]
    items = [dict(it, id=str(it.get("id", f"i{k}"))) for k, it in enumerate(items)]
    if not items:
        base = {"variant_id": variant_id, "kind": m["kind"], "n_items": 0}
        return base | ({"detected": False, "located": False, "matched_items": []} if m["kind"] == "planted"
                       else {"false_alarms": 0, "false_alarm_items": []})
    listing = "\n".join(_item_text(it) for it in items)
    if m["kind"] == "planted":
        ch = changed_words(m)
        qhit = {it["id"]: any(quote_hits(q.get("quote", ""), m["planted_span"], ch) or quote_hits(it.get("claim", ""), m["planted_span"], ch)
                              for q in (it.get("evidence") or [{}])) for it in items}
        j = _judge(JUDGE_PLANTED.format(type=m["type"], page=m["page"], original=m["original_span"], planted=m["planted_span"],
                                        detection=m["detection"], items=listing), f"{tag}:{variant_id}")
        per = []
        for it in items:
            r = j.get(it["id"], {})
            hit = bool(r.get("nature")) and (qhit[it["id"]] or bool(r.get("location")))
            per.append({"id": it["id"], "quote_hit": qhit[it["id"]], "judge_nature": bool(r.get("nature")),
                        "judge_location": bool(r.get("location")), "detects": hit, "reason": r.get("reason", "")})
        return {"variant_id": variant_id, "kind": "planted", "type": m["type"], "n_items": len(items),
                "detected": any(p["detects"] for p in per), "located": any(p["quote_hit"] for p in per),
                "matched_items": [p["id"] for p in per if p["detects"]], "items": per}
    twins = [man[t] for t in m["planted_twins"]]
    errors = "\n".join(f'{k+1}. Correct text: "{t["original_span"]}" -> planted wrong version: "{t["planted_span"]}". '
                       f'The planted error: {t["detection"]}' for k, t in enumerate(twins))
    j = _judge(JUDGE_CLEAN.format(errors=errors, items=listing), f"{tag}:{variant_id}")
    per = []
    for it in items:
        r = j.get(it["id"], {})
        a = r.get("asserts_error")
        a = int(a) if str(a).strip().isdigit() and 1 <= int(a) <= len(twins) else None
        near = a is not None and any(quote_hits(q.get("quote", ""), twins[a - 1]["original_span"], set(words(twins[a - 1]["original_span"])))
                                     for q in (it.get("evidence") or [{}]))
        per.append({"id": it["id"], "asserts_error_of": twins[a - 1]["variant_id"] if a else None,
                    "quotes_that_passage": near, "reason": r.get("reason", "")})
    fa = [p["id"] for p in per if p["asserts_error_of"]]
    return {"variant_id": variant_id, "kind": "clean", "n_items": len(items), "false_alarms": len(fa),
            "false_alarm_items": fa, "items": per}

def main(folder: str):
    man = load_manifest()
    d = Path(folder)
    res = [score_variant(f.stem, json.load(open(f)), man, tag=f"g4:{d.parent.name}") for f in sorted(d.glob("*.json")) if f.stem in man]
    out = ROOT / "runs/grades/g4" / f"{d.parent.name}.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    pl = [r for r in res if r["kind"] == "planted"]; cl = [r for r in res if r["kind"] == "clean"]
    print(f"{d.parent.name}: recall {sum(r['detected'] for r in pl)}/{len(pl)}, located {sum(r['located'] for r in pl)}/{len(pl)}, "
          f"false alarms on clean twins {sum(r['false_alarms'] for r in cl)} over {sum(r['n_items'] for r in cl)} items")

if __name__ == "__main__":
    main(sys.argv[1])
