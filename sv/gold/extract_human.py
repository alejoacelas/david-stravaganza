"""Expanded human reference set: atomic criticisms from each Unjournal evaluator report.

Step 1 (one Opus call per evaluator report): split the report into atomic criticisms,
each with a verbatim supporting quote from the report.
Step 2 (one Opus call per paper): label each criticism with whether the evaluation
manager's summary endorses it, how the author response treats it (conceded / rebutted /
not addressed), and which curated issues (uj_gold_issues.json) it corresponds to.
Every quote is then checked mechanically against its source (sources.verify).

Output: data/derived/uj_human_items.json keyed by paper id.
Run: uv run python -m sv.gold.extract_human
"""
import json
from concurrent.futures import ThreadPoolExecutor
from sv import llm
from sv.gold.sources import MAP, STUBS, ROOT, load, verify

OUT = ROOT / "data/derived/uj_human_items.json"
GOLD = json.loads((ROOT / "data/derived/uj_gold_issues.json").read_text())

EXTRACT_SYS = """You turn a peer-review report into a list of atomic criticisms, in the style of
Kim et al. (PeerReview Bench): each item names ONE specific aspect of the paper the reviewer finds
wrong, weak, unclear, missing or overstated. Split compound comments into separate items. Keep
suggestions only when they imply a weakness (e.g. "should add robustness check X" -> "results not
shown to be robust to X"). Leave out praise, summaries of the paper, pure rating justifications,
and remarks about the evaluation process.

For each item give:
- "criticism": one self-contained sentence a reader can understand without the report.
- "quote": a contiguous verbatim span copied character-for-character from the report (typically
  10-50 words) that shows the reviewer making this criticism. Do not stitch, paraphrase, fix typos
  or drop words; you may start or end mid-sentence. Avoid spans that cross table cells or footnote markers.
- "paper_location": the section/table/page of the paper the criticism targets, if the report says; else "".
- "severity_hint": "major" if the reviewer presents it as central to the paper's conclusions, else "minor".

Reply with only a JSON array of objects."""

LABEL_SYS = """You label a list of reviewer criticisms of one paper against three other documents:
the evaluation manager's summary, the authors' response (may be absent), and a curated list of
key issues written by the evaluation manager.

For each criticism return:
- "id": the criticism id.
- "manager_endorses": true if the manager summary repeats, highlights or agrees with this specific
  criticism; false if it does not mention it or disagrees. null if no manager summary is given.
- "manager_quote": verbatim span (10-50 words, copied character-for-character) from the manager
  summary supporting manager_endorses=true; "" otherwise.
- "author_label": "conceded" (authors accept the point, fix it, or acknowledge it as a limitation),
  "rebutted" (authors argue the point is wrong or does not matter), or "not addressed". null if
  no author response is given. If the authors partly accept and partly push back, choose the
  stance that dominates their reply to this specific point.
- "author_quote": verbatim span (10-50 words, copied character-for-character) from the author
  response supporting the label; "" if not addressed or no response.
- "curated_ids": list of curated issue ids (e.g. ["H2"]) that this criticism is part of or the same
  as; [] if none.

Reply with only a JSON array, one object per criticism, in the given order."""


def extract(pid: str, ev: str, fname: str) -> list[dict]:
    rep = load(fname)
    title = GOLD[pid]["title"]
    reply = llm.call(f"Paper: {title}\n\nReviewer report ({ev}):\n<report>\n{rep}\n</report>",
                     system=EXTRACT_SYS, max_tokens=16000, tag=f"gold-extract:{pid}:{ev}")
    items = llm.parse_json(reply)
    out = []
    for i, it in enumerate(items, 1):
        out.append({"id": f"{ev}-{i}", "evaluator": ev, "source_file": fname, **it,
                    "quote_verified": verify(it.get("quote", ""), rep)})
    return out


def label(pid: str, items: list[dict]) -> list[dict]:
    m = MAP[pid]
    summ, resp = load(m["summary"]), load(m["response"])
    cur = "\n".join(f"{h['id']}: {h['text']}" for h in GOLD[pid]["human_issues"])
    crit = "\n".join(f"{it['id']}: {it['criticism']}" for it in items)
    prompt = (f"Paper: {GOLD[pid]['title']}\n\n<criticisms>\n{crit}\n</criticisms>\n\n"
              f"<manager_summary>\n{summ or 'NONE GIVEN'}\n</manager_summary>\n\n"
              f"<author_response>\n{resp or 'NONE GIVEN'}\n</author_response>\n\n"
              f"<curated_issues>\n{cur}\n</curated_issues>")
    labs = {x["id"]: x for x in llm.parse_json(llm.call(prompt, system=LABEL_SYS, max_tokens=24000,
                                                         tag=f"gold-label:{pid}"))}
    for it in items:
        lab = labs.get(it["id"], {})
        it["manager_endorses"] = lab.get("manager_endorses") if summ else None
        it["manager_quote"] = lab.get("manager_quote", "") if summ else ""
        it["manager_quote_verified"] = verify(it["manager_quote"], summ) if it["manager_quote"] else None
        it["author_label"] = lab.get("author_label") if resp else None
        it["author_quote"] = lab.get("author_quote", "") if resp else ""
        it["author_quote_verified"] = verify(it["author_quote"], resp) if it["author_quote"] else None
        valid = {h["id"] for h in GOLD[pid]["human_issues"]}
        it["curated_ids"] = [c for c in lab.get("curated_ids", []) if c in valid]
        it["curated_ids_dropped"] = [c for c in lab.get("curated_ids", []) if c not in valid]
        it["label_missing"] = not lab
    return items


def run_paper(pid: str) -> tuple[str, dict]:
    m = MAP[pid]
    evs = [(e, f) for e, f in m["evaluators"].items() if f not in STUBS]
    with ThreadPoolExecutor(4) as ex:
        items = [x for lst in ex.map(lambda a: extract(pid, *a), evs) for x in lst]
    items = label(pid, items)
    return pid, {"title": GOLD[pid]["title"], "sources": m,
                 "stub_files_skipped": [f for f in m["evaluators"].values() if f in STUBS],
                 "curated_matching": "model call (Opus, gold-label step)", "items": items}


def main():
    with ThreadPoolExecutor(7) as ex:
        res = dict(ex.map(run_paper, MAP))
    OUT.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    for pid, r in res.items():
        print(pid, len(r["items"]))
    print("spent", round(llm.spent(), 2))


if __name__ == "__main__":
    main()
