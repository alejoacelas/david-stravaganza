"""Calibrate G3 on PeerReview Bench's 908 doubly-annotated items (27 papers).

uv run python -m sv.graders.calibrate_g3 {dev|test|all} [--model claude-opus-5-5]
Writes predictions to runs/calibration/preds/ and prints agreement tables as JSON.
"""
import json, random, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from sv import llm
from sv.graders import g3_quality
from sv.graders.agree import agreement

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/raw/peerreview-bench/json/meta_reviewer.json"
OUT = ROOT / "runs/calibration/preds"
SIG = {"Significant": "significant", "Marginally Significant": "marginal", "Not Significant": "not"}
CATS = {"correct": [True, False], "significance": ["significant", "marginal", "not"], "evidence_sufficient": [True, False]}


def human(r, who):
    c = r[f"correctness_{who}"]
    return {"correct": None if c is None else c == "Correct",
            "significance": SIG.get(r[f"significance_{who}"]),
            "evidence_sufficient": {"Sufficient": True, "Requires More": False}.get(r[f"evidence_{who}"])}


def split():
    ids = sorted(int(p) for p in json.load(open(DATA))["papers"])
    random.Random(20261110).shuffle(ids)
    return {"dev": sorted(ids[:9]), "test": sorted(ids[9:])}


def run(which, model=llm.OPUS):
    d = json.load(open(DATA))
    pids = split()[which] if which != "all" else sorted(int(p) for p in d["papers"])
    by = {p: [r for r in d["items"] if r["paper_id"] == p] for p in pids}

    def one(p):
        rows = sorted(by[p], key=lambda r: (r["reviewer_id"], r["review_item_number"]))
        try:
            preds = g3_quality.grade(d["papers"][str(p)], [{"text": r["review_item"]} for r in rows],
                                     model=model, tag=f"g3-cal-{g3_quality.VERSION}")
        except ValueError as e:  # e.g. paper 79 (chemistry synthesis): the API refuses; paper is excluded
            print(f"EXCLUDED paper {p}: {e}", file=sys.stderr)
            return []
        return [dict(paper_id=p, reviewer_id=r["reviewer_id"], reviewer_type=r["reviewer_type"],
                     item=r["review_item_number"], P=human(r, "primary"), S=human(r, "secondary"), M=m)
                for r, m in zip(rows, preds)]

    with ThreadPoolExecutor(6) as ex:
        recs = [x for res in ex.map(one, pids) for x in res]
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{g3_quality.VERSION}_{model}_{which}"
    (OUT / f"g3_{tag}.json").write_text(json.dumps(recs, indent=1))
    return recs


def tables(recs):
    out = {}
    for sub, rs in [("all", recs), ("human_items", [r for r in recs if r["reviewer_type"] == "Human"]),
                    ("ai_items", [r for r in recs if r["reviewer_type"] == "AI"])]:
        t = {}
        for dim, cats in CATS.items():
            g = lambda who: [r[who][dim] for r in rs]
            # Kim et al. protocol: accuracy vs primary on items where both annotators agree up to this stage
            stage = {"correct": ["correct"], "significance": ["correct", "significance"],
                     "evidence_sufficient": ["correct", "significance", "evidence_sufficient"]}[dim]
            agreed = [r for r in rs if all(r["P"][k] == r["S"][k] and r["P"][k] is not None for k in stage)]
            kim = agreement([r["M"][dim] if r["M"][dim] is not None else "__none__" for r in agreed],
                            [r["P"][dim] for r in agreed], cats + ["__none__"])
            t[dim] = {"P-S": agreement(g("P"), g("S"), cats), "M-P": agreement(g("M"), g("P"), cats),
                      "M-S": agreement(g("M"), g("S"), cats), "M_vs_agreed": {"n": kim["n"], "pct": kim["pct"]}}
        out[sub] = t
    return out


if __name__ == "__main__":
    which = sys.argv[1]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else llm.OPUS
    recs = run(which, model)
    print(json.dumps(tables(recs), indent=1))
    print("spent so far:", round(llm.spent(), 2))
