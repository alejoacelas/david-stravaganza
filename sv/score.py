"""Score every reviewer with the narrow graders and write runs/results/.

Unjournal set (14 papers):
  - G2 recall of the 43 curated human issues, and of all extracted evaluator criticisms.
  - G3 item quality (correct -> significant -> evidence sufficient), graded in one blind,
    shuffled pool per paper that mixes every reviewer's items with a sample of human items.
  - G1 share of quotes found verbatim in the paper.
  - "New valid finds": AI items rated fully positive by G3 that match no human criticism.
Planted set: G4 recall, location and false alarms on clean twins (runs per reviewer).

    uv run python -m sv.score uj R0a R0b R1 R2
    uv run python -m sv.score planted R0b R1 R2
"""
import json, random, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

from sv.graders import g2_match, g3_quality
from sv.gold import g1_evidence

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs/results"; OUT.mkdir(parents=True, exist_ok=True)
HUMAN_SAMPLE = 12  # human criticisms per paper added to the G3 pool


def load_reviews(rev, set_="uj"):
    d = ROOT / "runs/reviews" / rev / set_
    return {f.stem: json.load(open(f)) for f in sorted(d.glob("*.json"))}


def human_items(pid, hum):
    out = []
    for it in hum[pid]["items"]:
        out.append({"id": it["id"], "text": it["criticism"] + (f'\nFrom the evaluator\'s report: "{it["quote"]}"' if it.get("quote") else "")})
    return out


def boot_ci(per_paper_num, per_paper_den, n=2000, seed=0):
    """Ratio estimate with a paper-clustered bootstrap 95% CI."""
    num, den = np.array(per_paper_num, float), np.array(per_paper_den, float)
    if den.sum() == 0:
        return None, None, None
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(num), (n, len(num)))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = num[idx].sum(1) / den[idx].sum(1)
    bs = bs[~np.isnan(bs)]
    return num.sum() / den.sum(), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def score_uj(revs):
    gold = json.load(open(ROOT / "data/derived/uj_gold_issues.json"))
    hum = json.load(open(ROOT / "data/derived/uj_human_items.json"))
    reviews = {r: load_reviews(r) for r in revs}
    pids = sorted(gold)
    rng = random.Random(0)
    per = {}  # pid -> rev -> metrics

    def do_paper(pid):
        paper = (ROOT / "data/papers" / f"{pid}.txt").read_text()
        curated = [{"id": h["id"], "text": h["text"]} for h in gold[pid]["human_issues"]]
        hitems = human_items(pid, hum)
        res = {}
        # G3: one blind pool per paper, shuffled across sources
        pool = []
        for r in revs:
            for it in reviews[r].get(pid, []):
                pool.append((r, it))
        hs = random.Random(pid).sample(hitems, min(HUMAN_SAMPLE, len(hitems)))
        pool += [("HUMAN", it) for it in hs]
        random.Random(pid + "shuffle").shuffle(pool)
        grades = g3_quality.grade(paper, [it for _, it in pool], tag=f"score:g3:{pid}")
        for r in revs + ["HUMAN"]:
            gs = [(it, g) for (src, it), g in zip(pool, grades) if src == r]
            res[r] = {"n": len(gs),
                      "correct": sum(g["correct"] is True for _, g in gs),
                      "significant": sum(g["correct"] is True and g["significance"] == "significant" for _, g in gs),
                      "full": sum(g["correct"] is True and g["significance"] == "significant" and g["evidence_sufficient"] is True for _, g in gs),
                      "full_ids": [it.get("id") for it, g in gs if g["correct"] is True and g["significance"] == "significant" and g["evidence_sufficient"] is True]}
        # G2 recall + G1 evidence, per AI reviewer
        for r in revs:
            items = reviews[r].get(pid, [])
            m_cur = g2_match.match_lists(pid, items, curated, tag=f"score:g2cur:{r}:{pid}") if items else {}
            m_all = g2_match.match_lists(pid, items, hitems, tag=f"score:g2all:{r}:{pid}") if items else {}
            matched_ai = {m["ai_id"] for ms in m_all.values() for m in ms}
            quotes = [q for it in items if it.get("evidence") for q in g1_evidence.check(paper, it)]
            res[r].update({
                "curated_n": len(curated), "curated_hit": sum(bool(m_cur.get(c["id"])) for c in curated),
                "human_n": len(hitems), "human_hit": sum(bool(m_all.get(h["id"])) for h in hitems),
                "new_valid": sum(i not in matched_ai for i in res[r]["full_ids"]),
                "quotes_n": len(quotes), "quotes_found": sum(q["found"] for q in quotes),
                "unmatched_ids": [it.get("id") for it in items if it.get("id") not in matched_ai],
            })
        return pid, res

    with ThreadPoolExecutor(4) as ex:
        for pid, res in ex.map(do_paper, pids):
            per[pid] = res
            print("scored", pid, flush=True)
    (OUT / "uj_per_paper.json").write_text(json.dumps(per, indent=1))

    rows = []
    for r in revs + ["HUMAN"]:
        def agg(num, den):
            v, lo, hi = boot_ci([per[p][r].get(num, 0) for p in pids], [per[p][r].get(den, 0) if isinstance(den, str) else den for p in pids])
            return None if v is None else {"v": round(v, 3), "lo": round(lo, 3), "hi": round(hi, 3)}
        row = {"reviewer": r, "items": sum(per[p][r]["n"] for p in pids),
               "correct": agg("correct", "n"), "significant": agg("significant", "n"), "fully_positive": agg("full", "n"),
               "fully_positive_per_paper": round(np.mean([per[p][r]["full"] for p in pids]), 2)}
        if r != "HUMAN":
            row.update({"curated_recall": agg("curated_hit", "curated_n"), "human_item_recall": agg("human_hit", "human_n"),
                        "new_valid_per_paper": round(np.mean([per[p][r]["new_valid"] for p in pids]), 2),
                        "quotes_found": agg("quotes_found", "quotes_n")})
        rows.append(row)
    (OUT / "uj_summary.json").write_text(json.dumps(rows, indent=1))
    return rows


def score_planted(revs):
    from sv.planted import g4_score
    rows = []
    for r in revs:
        g4_score.main(str(ROOT / "runs/reviews" / r / "planted"))
        res = json.load(open(ROOT / "runs/grades/g4" / f"{r}.json"))
        pl = [x for x in res if x["kind"] == "planted"]; cl = [x for x in res if x["kind"] == "clean"]
        rows.append({"reviewer": r, "variants": len(pl), "detected": sum(x["detected"] for x in pl),
                     "located": sum(x["located"] for x in pl), "clean_twins": len(cl),
                     "false_alarms": sum(x["false_alarms"] for x in cl),
                     "clean_twins_with_false_alarm": sum(x["false_alarms"] > 0 for x in cl),
                     "items_per_text": round(np.mean([x["n_items"] for x in res]), 1),
                     "by_type": {t: f'{sum(x["detected"] for x in pl if x["type"] == t)}/{sum(x["type"] == t for x in pl)}'
                                 for t in sorted({x["type"] for x in pl})}})
    (OUT / "planted_summary.json").write_text(json.dumps(rows, indent=1))
    return rows


if __name__ == "__main__":
    set_, revs = sys.argv[1], sys.argv[2:]
    rows = score_uj(revs) if set_ == "uj" else score_planted(revs)
    print(json.dumps(rows, indent=1))
