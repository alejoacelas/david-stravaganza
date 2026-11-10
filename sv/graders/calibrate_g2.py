"""Calibrate G2 on PeerReview Bench's 164-pair similarity set and Reinstein's 3 annotations.

uv run python -m sv.graders.calibrate_g2 {dev|test|all} [--model M] [--mode pair|list|both]
Pair mode: one call per labelled pair. List mode: one match_lists call per paper with all
B items as reference issues and all A items as AI items, read out at the labelled pairs.
"""
import json, math, random, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from sv import llm
from sv.graders import g2_match
from sv.graders.agree import agreement

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/raw/peerreview-bench/json/similarity_check.json"
REIN = ROOT / "data/raw/llm-uj-research-eval/data/human_issue_match_annotations/issue_annotations_reinstein.json"
BASE = ROOT / "data/derived/uj_baseline_gpt52pro_issues.json"
OUT = ROOT / "runs/calibration/preds"
FOUR = {"same subject, same argument, same evidence": "same_issue_same_reasoning",
        "same subject, same argument, different evidence": "same_issue_different_reasoning",
        "same subject, different argument": "same_target_different_criticism",
        "different subject": "different_target"}


def split():
    ids = sorted(int(p) for p in json.load(open(DATA))["papers"])
    random.Random(20261110).shuffle(ids)
    return {"dev": sorted(ids[:11]), "test": sorted(ids[11:])}


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(100 * (c - h), 1), round(100 * (c + h), 1)]


def key(p, side):
    return f'{p[f"item_{side}_reviewer_id"]}#{p[f"item_{side}_item_number"]}'


def run(which, model=llm.OPUS, mode="both"):
    d = json.load(open(DATA))
    pids = set(split()[which] if which != "all" else [int(x) for x in d["papers"]])
    pairs = [p for p in d["pairs"] if p["paper_id"] in pids]
    recs = [{"pair": p["eval_pair_id"], "paper_id": p["paper_id"], "pair_type": p["pair_type"],
             "gold": p["binary_label"] == "similar", "gold4": FOUR[p["finegrained_label"]]} for p in pairs]
    if mode in ("pair", "both"):
        with ThreadPoolExecutor(8) as ex:
            res = list(ex.map(lambda p: g2_match.match(p["item_a_text"], p["item_b_text"], model=model,
                                                       tag=f"g2-cal-pair-{g2_match.VERSION}"), pairs))
        for r, m in zip(recs, res):
            r["pair_pred"] = m
    if mode in ("list", "both"):
        def one(pid):
            pp = [p for p in pairs if p["paper_id"] == pid]
            ai = {key(p, "a"): p["item_a_text"] for p in pp}; ref = {key(p, "b"): p["item_b_text"] for p in pp}
            return pid, g2_match.match_lists(pid, [{"id": k, "text": v} for k, v in ai.items()],
                                             [{"id": k, "text": v} for k, v in ref.items()], model=model,
                                             tag=f"g2-cal-list-{g2_match.VERSION}")
        with ThreadPoolExecutor(8) as ex:
            lists = dict(ex.map(one, sorted(pids)))
        for r, p in zip(recs, pairs):
            ms = lists[p["paper_id"]][key(p, "b")]
            r["list_pred"] = any(m["ai_id"] == key(p, "a") for m in ms)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"g2_{g2_match.VERSION}_{model}_{which}_{mode}.json").write_text(json.dumps(recs, indent=1))
    return recs


def summarize(recs):
    out = {}
    for mode, get in [("pair", lambda r: r["pair_pred"]["match"]), ("list", lambda r: r["list_pred"])]:
        if not recs or (mode == "pair" and "pair_pred" not in recs[0]) or (mode == "list" and "list_pred" not in recs[0]):
            continue
        g = [r["gold"] for r in recs]; m = [get(r) for r in recs]
        k = sum(a == b for a, b in zip(g, m)); n = len(g)
        s = {"binary": agreement(m, g, [True, False]), "acc_ci95": wilson(k, n),
             "sensitivity": round(100 * sum(a and b for a, b in zip(g, m)) / max(1, sum(g)), 1),
             "specificity": round(100 * sum((not a) and (not b) for a, b in zip(g, m)) / max(1, n - sum(g)), 1)}
        for pt in ("AI-AI", "AI-Human"):
            sub = [(a, b) for a, b, r in zip(g, m, recs) if r["pair_type"] == pt]
            s[f"acc_{pt}"] = round(100 * sum(a == b for a, b in sub) / max(1, len(sub)), 1)
        if mode == "pair":
            s["fourway_acc"] = round(100 * sum(r["pair_pred"]["relation"] == r["gold4"] for r in recs) / n, 1)
        out[mode] = s
    return out


def reinstein(model=llm.OPUS):
    """Reinstein's 3 Acemoglu annotations: human issue vs GPT-5.2 Pro's list (L<n> = B<n>)."""
    rows = json.load(open(REIN))["rows"]
    base = json.load(open(BASE))["Acemoglu_et_al._2024"]
    ai = [{"id": f'L{b["id"][1:]}', "text": b["claim"]} for b in base]
    ref = [{"id": r["human_issue_id"], "text": r["human_issue_text"]} for r in rows]
    res = g2_match.match_lists("Acemoglu_et_al._2024", ai, ref, model=model, tag=f"g2-cal-rein-{g2_match.VERSION}")
    return [{"issue": r["human_issue_id"], "human_score": r["match_score"], "human_ids": r["llm_issue_ids"],
             "grader": res[r["human_issue_id"]]} for r in rows]


if __name__ == "__main__":
    which = sys.argv[1]
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else llm.OPUS
    mode = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "both"
    if which == "reinstein":
        print(json.dumps(reinstein(model), indent=1))
    else:
        print(json.dumps(summarize(run(which, model, mode)), indent=1))
    print("spent so far (all workstreams):", round(llm.spent(), 2))
