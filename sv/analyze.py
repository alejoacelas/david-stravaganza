"""Follow-up analyses on top of sv.score (G2 calls are served from the cache).

1. Recall at equal list length: each reviewer's first k items only (k = 5, 10), so longer
   lists don't win by volume.
2. Quote check restricted to items that carry quotes (R0a/R0b carry none).
3. Grader sanity check: G3 on the 43 curated Unjournal key issues. These were picked by
   the evaluation manager as the papers' key problems, so a grader that is calibrated
   for this domain should rate most of them correct and significant.
4. Run-to-run stability: share of R1 seed-1 and seed-2 items that match a seed-0 item.

    uv run python -m sv.analyze
"""
import json
from pathlib import Path
import numpy as np

from sv.graders import g2_match, g3_quality
from sv.gold import g1_evidence
from sv.score import load_reviews, human_items, boot_ci

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "runs/results"
REVS = ["R0a", "R0b", "R1", "R2"]


def main():
    gold = json.load(open(ROOT / "data/derived/uj_gold_issues.json"))
    hum = json.load(open(ROOT / "data/derived/uj_human_items.json"))
    pids = sorted(gold)
    reviews = {r: load_reviews(r) for r in REVS + ["R1s1", "R1s2"]}
    out = {}

    # 1. recall at equal length
    rec = {}
    for r in REVS:
        for k in (5, 10, None):
            hits_c, n_c, hits_h, n_h = [], [], [], []
            for pid in pids:
                items = reviews[r].get(pid, [])
                keep = {it["id"] for it in (items[:k] if k else items)}
                curated = [{"id": h["id"], "text": h["text"]} for h in gold[pid]["human_issues"]]
                hitems = human_items(pid, hum)
                mc = g2_match.match_lists(pid, items, curated, tag=f"score:g2cur:{r}:{pid}") if items else {}
                mh = g2_match.match_lists(pid, items, hitems, tag=f"score:g2all:{r}:{pid}") if items else {}
                hits_c.append(sum(any(m["ai_id"] in keep for m in mc.get(c["id"], [])) for c in curated)); n_c.append(len(curated))
                hits_h.append(sum(any(m["ai_id"] in keep for m in mh.get(h["id"], [])) for h in hitems)); n_h.append(len(hitems))
            rec[f"{r}@{k or 'all'}"] = {"curated": [round(x, 3) for x in boot_ci(hits_c, n_c)],
                                        "human_items": [round(x, 3) for x in boot_ci(hits_h, n_h)]}
    out["recall_at_k"] = rec

    # 2. quotes, only items that carry quotes
    q = {}
    for r in REVS:
        found = n = items_with = 0
        for pid in pids:
            paper = (ROOT / "data/papers" / f"{pid}.txt").read_text()
            for it in reviews[r].get(pid, []):
                if it.get("evidence"):
                    items_with += 1
                    res = g1_evidence.check(paper, it)
                    n += len(res); found += sum(x["found"] for x in res)
        q[r] = {"items_with_quotes": items_with, "quotes": n, "found": found}
    out["quotes"] = q

    # 3. G3 on curated key issues
    cur = {"n": 0, "correct": 0, "significant": 0, "full": 0, "by_severity": {}}
    for pid in pids:
        paper = (ROOT / "data/papers" / f"{pid}.txt").read_text()
        issues = gold[pid]["human_issues"]
        gs = g3_quality.grade(paper, [{"id": h["id"], "text": h["text"]} for h in issues], tag=f"sanity:g3cur:{pid}")
        for h, g in zip(issues, gs):
            c, s = g["correct"] is True, g["correct"] is True and g["significance"] == "significant"
            f = s and g["evidence_sufficient"] is True
            cur["n"] += 1; cur["correct"] += c; cur["significant"] += s; cur["full"] += f
            b = cur["by_severity"].setdefault(h.get("severity", "?"), {"n": 0, "significant": 0})
            b["n"] += 1; b["significant"] += s
    out["g3_on_curated_issues"] = cur

    # 4. stability across R1 seeds
    st = {}
    for s in ("R1s1", "R1s2"):
        num = den = 0
        for pid in pids:
            ref = reviews["R1"].get(pid, []); other = reviews[s].get(pid, [])
            if not ref or not other:
                continue
            try:
                m = g2_match.match_lists(pid, ref, [{"id": it["id"], "text": it["claim"]} for it in other], tag=f"stab:{s}:{pid}")
            except Exception as e:  # e.g. API credit exhausted; report the papers covered
                print("stability skipped for", s, pid, type(e).__name__)
                continue
            num += sum(bool(m.get(it["id"])) for it in other); den += len(other)
        st[s] = {"items": den, "matching_a_seed0_item": num, "share": round(num / den, 3) if den else None}
    out["stability"] = st

    (OUT / "uj_analysis.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
