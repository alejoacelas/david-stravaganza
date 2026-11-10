"""Calibrate G1 (sv/gold/g1_evidence.py) on true quotes vs perturbed fakes from the 14 papers.

True quotes: random 8-40 word spans of the page text, cleaned the way a reviewer would copy
them (whitespace collapsed; for half, line-end hyphenation joined and ligatures expanded),
plus table-ish spans (high digit share). OCR variants: true quotes with 1-3 character-level
errors (l/1, rn/m, O/0, dropped or doubled letter, ligature, stray space).
Fakes: one number changed; one or two words replaced or two adjacent words swapped; spans
spliced from two places in the paper; Haiku paraphrases (light: 2-4 words changed; full).

Papers are split 7/7: the threshold is chosen on the first half and reported on the second.
Run: uv run python -m sv.gold.g1_calibrate
"""
import json, random, re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from sv import llm
from sv.gold.sources import ROOT
from sv.gold import g1_evidence as g1

PAPERS = ROOT / "data/papers"
OUT = ROOT / "data/derived/g1_calibration.json"
rng = random.Random(20261110)


def pages_of(text):
    parts = g1.PAGE_RE.split(text)
    return [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def reviewer_copy(raw: str, tidy: bool) -> str:
    s = raw
    if tidy:
        import unicodedata
        s = re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", s)
        s = unicodedata.normalize("NFKC", s)
    return re.sub(r"\s+", " ", s).strip()


def sample_span(pages, n_words, tableish=False, tries=200):
    for _ in range(tries):
        pg, txt = rng.choice(pages)
        toks = list(re.finditer(r"\S+", txt))
        if len(toks) < n_words + 5:
            continue
        i = rng.randrange(0, len(toks) - n_words)
        raw = txt[toks[i].start():toks[i + n_words - 1].end()]
        digits = sum(c.isdigit() for c in raw) / max(1, len(raw.replace(" ", "")))
        if tableish and digits < 0.25:
            continue
        if not tableish and digits > 0.15:
            continue
        if len(raw) < 40:
            continue
        return pg, raw
    return None


def change_number(q):
    nums = list(re.finditer(r"\d+(?:\.\d+)?", q))
    if not nums:
        return None
    m = rng.choice(nums)
    s = m.group()
    digs = [k for k, c in enumerate(s) if c.isdigit()]
    k = rng.choice(digs)
    new = s[:k] + str((int(s[k]) + rng.randint(1, 8)) % 10) + s[k + 1:]
    return q[:m.start()] + new + q[m.end():]


def swap_words(q, vocab):
    w = q.split(" ")
    content = [k for k, t in enumerate(w) if len(t) >= 4 and t.isalpha()]
    if len(content) < 2:
        return None
    mode = rng.choice(["replace1", "replace2", "transpose"])
    if mode == "transpose":
        k = rng.randrange(0, len(w) - 1)
        if w[k] == w[k + 1]:
            return None
        w[k], w[k + 1] = w[k + 1], w[k]
    else:
        for k in rng.sample(content, 1 if mode == "replace1" else 2):
            new = rng.choice(vocab)
            while new.lower() == w[k].lower():
                new = rng.choice(vocab)
            w[k] = new
    return " ".join(w), mode


def ocr_noise(q):
    ops = [("l", "1"), ("1", "l"), ("rn", "m"), ("m", "rn"), ("O", "0"), ("0", "O"), ("fi", "ﬁ"), ("e", "c"),
           ("i", "í")]
    s = q
    for _ in range(rng.randint(1, 3)):
        kind = rng.choice(["sub", "drop", "double", "space"])
        if kind == "sub":
            cand = [(a, b) for a, b in ops if a in s]
            if cand:
                a, b = rng.choice(cand)
                idxs = [m.start() for m in re.finditer(re.escape(a), s)]
                j = rng.choice(idxs)
                s = s[:j] + b + s[j + len(a):]
                continue
        letters = [k for k, c in enumerate(s) if c.isalpha()] or [k for k, c in enumerate(s) if not c.isspace()]
        j = rng.choice(letters)
        if kind == "drop":
            s = s[:j] + s[j + 1:]
        elif kind == "double":
            s = s[:j] + s[j] + s[j:]
        else:
            s = s[:j] + " " + s[j:]
    return s


PARA_SYS = """You rewrite text spans for a test of a quote checker. For each numbered span, return
a rewritten version. Mode LIGHT: change only 2-4 words (synonyms or small rewordings), keep
everything else identical. Mode FULL: paraphrase the whole span so the meaning is the same but the
wording differs. Keep numbers unchanged. Reply with only a JSON array of strings in input order."""


def paraphrase(spans, mode):
    out = []
    for b in range(0, len(spans), 20):
        batch = spans[b:b + 20]
        prompt = f"Mode: {mode}\n\n" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(batch))
        res = llm.parse_json(llm.call(prompt, system=PARA_SYS, model=llm.HAIKU, max_tokens=8000,
                                      tag=f"gold-g1-para-{mode}"))
        out += res[:len(batch)] + [None] * (len(batch) - len(res))
    return out


def build():
    cases = []
    for f in sorted(PAPERS.glob("*.txt")):
        pid, text = f.stem, f.read_text()
        pages = pages_of(text)
        vocab = sorted({w for w in re.findall(r"[A-Za-z]{4,}", text)})
        truths = []
        for k in range(22):
            r = sample_span(pages, rng.randint(8, 40))
            if r:
                truths.append((r[0], reviewer_copy(r[1], tidy=k % 2 == 0), "prose"))
        for k in range(8):
            r = sample_span(pages, rng.randint(8, 25), tableish=True)
            if r:
                truths.append((r[0], reviewer_copy(r[1], tidy=True), "table"))
        for pg, q, kind in truths:
            cases.append({"paper": pid, "quote": q, "page": pg, "label": True, "kind": f"true_{kind}"})
        for pg, q, kind in rng.sample(truths, 10):
            cases.append({"paper": pid, "quote": ocr_noise(q), "page": pg, "label": True, "kind": "true_ocr"})
        # page test: true quote with a wrong claimed page
        for pg, q, kind in rng.sample(truths, 5):
            cases.append({"paper": pid, "quote": q, "page": pg + rng.choice([-3, -2, 2, 3]), "label": True,
                          "kind": "true_wrongpage"})
        numbered = [t for t in truths if re.search(r"\d", t[1])]
        for pg, q, kind in rng.sample(numbered, min(8, len(numbered))):
            cases.append({"paper": pid, "quote": change_number(q), "page": pg, "label": False,
                          "kind": f"fake_number_{kind}"})
        n = 0
        for pg, q, kind in rng.sample(truths, len(truths)):
            r = swap_words(q, vocab)
            if r:
                cases.append({"paper": pid, "quote": r[0], "page": pg, "label": False, "kind": f"fake_swap_{r[1]}"})
                n += 1
            if n >= 9:
                break
        for _ in range(6):
            a, b = sample_span(pages, 24), sample_span(pages, 24)
            wa, wb = reviewer_copy(a[1], True).split(" "), reviewer_copy(b[1], True).split(" ")
            k = rng.randint(6, 14)
            cases.append({"paper": pid, "quote": " ".join(wa[:k] + wb[k:]), "page": a[0], "label": False,
                          "kind": "fake_splice"})
        prose = [t for t in truths if t[2] == "prose"]
        for mode in ("LIGHT", "FULL"):
            pick = rng.sample(prose, 6)
            cases.append({"paper": pid, "_para": mode, "_src": [p[1] for p in pick], "_pg": [p[0] for p in pick]})
    # paraphrases in batches across papers
    final, para_jobs = [], defaultdict(list)
    for c in cases:
        if "_para" in c:
            for q, pg in zip(c["_src"], c["_pg"]):
                para_jobs[c["_para"]].append((c["paper"], q, pg))
        else:
            final.append(c)
    for mode, jobs in para_jobs.items():
        res = paraphrase([j[1] for j in jobs], mode)
        for (pid, q, pg), p in zip(jobs, res):
            if p and g1.norm(p) != g1.norm(q):
                final.append({"paper": pid, "quote": p, "page": pg, "label": False,
                              "kind": f"fake_para_{mode.lower()}", "orig": q})
    return final


def score_all(cases):
    texts = {f.stem: f.read_text() for f in PAPERS.glob("*.txt")}

    def one(c):
        return {**c, **g1.check_quote(texts[c["paper"]], c["quote"], c["page"])}
    with ThreadPoolExecutor(8) as ex:
        return list(ex.map(one, cases))


def pred_of(r, T, E=0, rules=True):
    if not rules:
        return r["score"] >= T
    return r["score"] >= T and r["numbers_ok"] and len(r["word_edits"]) <= E


def prf(rows, T, E=0, rules=True):
    tp = fp = fn = tn = 0
    for r in rows:
        if r["kind"] == "true_wrongpage":
            continue
        pred = pred_of(r, T, E, rules)
        if r["label"] and pred: tp += 1
        elif r["label"]: fn += 1
        elif pred: fp += 1
        else: tn += 1
    p = tp / max(1, tp + fp); rc = tp / max(1, tp + fn)
    return {"precision": round(p, 3), "recall": round(rc, 3), "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "fake_rejection": round(tn / max(1, tn + fp), 3)}


def main():
    cases = build()
    rows = score_all(cases)
    papers = sorted({r["paper"] for r in rows})
    calib = set(papers[0::2])
    cal = [r for r in rows if r["paper"] in calib]
    hold = [r for r in rows if r["paper"] not in calib]
    grid = [(x / 2, E) for x in range(140, 201) for E in (0, 1)]
    def bal(rows_, T, E=0, rules=True):
        m = prf(rows_, T, E, rules); return (m["recall"] + m["fake_rejection"]) / 2
    T, E = max(grid, key=lambda g: (bal(cal, *g), -g[0], -g[1]))
    Tb = max([g[0] for g in grid], key=lambda t: (bal(cal, t, rules=False), -t))
    res = {"threshold": T, "max_word_edits": E, "n_cases": len(rows), "counts": Counter(r["kind"] for r in rows),
           "calibration_papers": sorted(calib), "calibration": prf(cal, T, E), "heldout": prf(hold, T, E),
           "baseline_partial_ratio_only": {"threshold": Tb, "heldout": prf(hold, Tb, rules=False)},
           "heldout_by_kind": {}}
    for k in sorted({r["kind"] for r in hold}):
        rs = [r for r in hold if r["kind"] == k]
        pred = [pred_of(r, T, E) for r in rs]
        res["heldout_by_kind"][k] = {"n": len(rs), "judged_found": round(sum(pred) / len(rs), 3)}
    tr = [r for r in hold if r["kind"] in ("true_prose", "true_table", "true_ocr") and pred_of(r, T, E)]
    wp = [r for r in hold if r["kind"] == "true_wrongpage" and pred_of(r, T, E)]
    res["page_ok_rate_true_page"] = round(sum(bool(r["page_claimed_ok"]) for r in tr) / max(1, len(tr)), 3)
    res["page_ok_rate_wrong_page"] = round(sum(bool(r["page_claimed_ok"]) for r in wp) / max(1, len(wp)), 3)
    res["score_quantiles_heldout"] = {k: sorted(r["score"] for r in hold if r["kind"] == k) for k in
                                      sorted({r["kind"] for r in hold})}
    OUT.write_text(json.dumps({"summary": res, "rows": rows}, indent=1, ensure_ascii=False))
    s = {k: v for k, v in res.items() if k != "score_quantiles_heldout"}
    print(json.dumps(s, indent=1))
    print("spent", round(llm.spent(), 2))


if __name__ == "__main__":
    main()
