"""Run a reviewer over a paper set.

    uv run python -m sv.reviewers.run --reviewer R1 --set uj [--seed 0]

Reviewers: R0a (published baseline, set uj only), R0b (one-shot key issues), R1 (structured
critique; --seed picks the run, saved as R1s<seed>, seed 0 also as R1), R2 (R1 seeds 0-2 pooled
and verified). Writes runs/reviews/<reviewer>/<set>/<paper_id>.json (a list of items) and a
sidecar runs/reviews/<reviewer>/<set>/_meta/<paper_id>.json (raw reply, notes, errors).
"""
import argparse, json, sys, traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from sv import llm
from sv.reviewers import prompts as P

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "reviews"
MAX_CHARS = 600_000  # ~150k tokens; longer papers are truncated with a note
EFFORT = "high"


def load_set(name: str) -> dict[str, str]:
    if name == "uj":
        ids = json.load(open(ROOT / "data/derived/uj_gold_issues.json")).keys()
        return {i: (ROOT / "data/papers" / f"{i}.txt").read_text() for i in ids}
    if name == "planted":
        man = ROOT / "data/planted/manifest.json"
        if not man.exists():
            sys.exit("data/planted/manifest.json not found")
        m = json.load(open(man))
        entries = m.get("variants", m) if isinstance(m, dict) else m
        if isinstance(entries, dict):
            entries = [{"id": k, **(v if isinstance(v, dict) else {"text": v})} for k, v in entries.items()]
        out = {}
        for e in entries:
            vid = e.get("id") or e.get("variant_id")
            path = e.get("text") or e.get("text_path") or e.get("path")
            p = Path(path)
            p = p if p.is_absolute() else (ROOT / p if (ROOT / p).exists() else ROOT / "data/planted" / p)
            out[vid] = p.read_text()
        return out
    sys.exit(f"unknown set {name}")


def prep(text: str) -> tuple[str, str]:
    if len(text) <= MAX_CHARS:
        return text, ""
    return text[:MAX_CHARS], f"truncated from {len(text)} to {MAX_CHARS} chars"


def write(reviewer, set_, pid, items, meta):
    d = OUT / reviewer / set_
    (d / "_meta").mkdir(parents=True, exist_ok=True)
    (d / f"{pid}.json").write_text(json.dumps(items, indent=1, ensure_ascii=False))
    (d / "_meta" / f"{pid}.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))


def norm_items(raw, prefix):
    items = []
    for it in raw[:10]:
        ev = [{"quote": str(e.get("quote", "")), "page": e.get("page")} for e in it.get("evidence", [])][:3]
        items.append({"id": f"{prefix}-{len(items)+1}", "claim": it.get("claim", ""),
                      "severity": it.get("severity"), "consequence": it.get("consequence", ""),
                      "evidence": ev})
    return items


def paper_system(text):
    t, note = prep(text)
    return P.PAPER_SYSTEM.format(paper=t, note=f" NOTE: the paper text was {note}." if note else ""), note


def r1_call(pid, text, seed):
    system, note = paper_system(text)
    reply = llm.call(P.R1_USER, system=system, effort=EFFORT, max_tokens=32000,
                     tag=f"rev:R1:{pid}:s{seed}", seed=seed)
    raw = llm.parse_json(reply)
    if isinstance(raw, dict):
        raw = next(v for v in raw.values() if isinstance(v, list))
    return raw, reply, note


def run_r0a(set_, pid, text):
    base = json.load(open(ROOT / "data/derived/uj_baseline_gpt52pro_issues.json"))[pid]
    items = [{"id": f"R0a-{i+1}", "claim": b["claim"]} for i, b in enumerate(base)]
    write("R0a", set_, pid, items, {"source": "data/derived/uj_baseline_gpt52pro_issues.json"})
    return len(items)


def run_r0b(set_, pid, text, seed=0):
    t, note = prep(text)
    reply = llm.call(P.R0B_USER.format(paper=t), system=P.R0B_SYSTEM, effort=EFFORT, max_tokens=32000,
                     tag=f"rev:R0b:{pid}:s{seed}", seed=seed, cache_system=False)
    raw = llm.parse_json(reply)
    issues = raw["key_issues"] if isinstance(raw, dict) else raw
    items = [{"id": f"R0b-{i+1}", "claim": str(c)} for i, c in enumerate(issues)]
    write("R0b", set_, pid, items, {"prompt_source": P.R0B_SOURCE, "note": note, "seed": seed, "reply": reply})
    return len(items)


def run_r1(set_, pid, text, seed=0):
    raw, reply, note = r1_call(pid, text, seed)
    name = f"R1s{seed}"
    items = norm_items(raw, name)
    write(name, set_, pid, items, {"note": note, "seed": seed, "reply": reply})
    if seed == 0:
        write("R1", set_, pid, [dict(it, id=it["id"].replace("R1s0", "R1")) for it in items],
              {"note": note, "seed": 0, "alias_of": "R1s0"})
    return len(items)


def run_r2(set_, pid, text, seed=0):
    # Seed 0 first so its call writes the prompt cache that seeds 1, 2 and the verifier read.
    runs = [r1_call(pid, text, 0)]
    with ThreadPoolExecutor(2) as ex:
        runs += list(ex.map(lambda s: r1_call(pid, text, s), (1, 2)))
    pooled = [it for s, (raw, _, _) in enumerate(runs) for it in norm_items(raw, f"s{s}")]
    system, note = paper_system(text)
    reply = llm.call(P.VERIFY_USER.format(items=json.dumps(pooled, indent=1, ensure_ascii=False)),
                     system=system, effort=EFFORT, max_tokens=32000, tag=f"rev:R2verify:{pid}")
    out = llm.parse_json(reply)
    items = norm_items(out["final"], "R2")
    for it, f in zip(items, out["final"]):
        it["source_ids"] = f.get("source_ids", [])
    write("R2", set_, pid, items, {"note": note, "pooled_n": len(pooled), "pooled": pooled,
                                    "decisions": out.get("decisions", []), "reply": reply})
    return len(items)


RUNNERS = {"R0a": run_r0a, "R0b": run_r0b, "R1": run_r1, "R2": run_r2}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reviewer", required=True, choices=list(RUNNERS))
    ap.add_argument("--set", required=True, choices=["uj", "planted"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--only", nargs="*", help="paper ids to run (default all)")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    if a.reviewer == "R0a" and a.set != "uj":
        sys.exit("R0a exists only for set uj")
    papers = load_set(a.set)
    if a.only:
        papers = {k: v for k, v in papers.items() if k in a.only}
    fn = RUNNERS[a.reviewer]
    kw = {} if a.reviewer == "R0a" else {"seed": a.seed}

    def one(pid):
        try:
            return pid, fn(a.set, pid, papers[pid], **kw), None
        except Exception as e:
            return pid, None, f"{type(e).__name__}: {e}\n{traceback.format_exc()[-800:]}"

    fails = []
    with ThreadPoolExecutor(min(a.workers, 6)) as ex:
        for pid, n, err in ex.map(one, papers):
            print(pid, n if err is None else "FAILED " + err.splitlines()[0], flush=True)
            if err:
                fails.append({"paper": pid, "error": err})
    name = f"R1s{a.seed}" if a.reviewer == "R1" else a.reviewer
    if fails:
        d = OUT / name / a.set; d.mkdir(parents=True, exist_ok=True)
        (d / "_failures.json").write_text(json.dumps(fails, indent=1))
    print(f"done: {len(papers) - len(fails)}/{len(papers)} ok; ledger total ${llm.spent():.2f}")


if __name__ == "__main__":
    main()
