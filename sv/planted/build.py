"""Build the planted-error benchmark: for each paper one clean twin and two variants with one planted error each.

Input: data/planted/edits.json (hand-checked edit spec; git-ignored because it quotes the papers)
       data/planted/text/<paper_id>.txt (from sv/planted/extract.py)
Output: data/planted/variants/<variant_id>.txt and data/planted/manifest.json

Variant ids are opaque (P01-x) and the clean twin is shuffled among them, so a file name
does not reveal which copy is clean.
"""
import json, random, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/planted"
VAR = D / "variants"; VAR.mkdir(parents=True, exist_ok=True)

def span_pattern(s: str) -> re.Pattern:
    """Match a span regardless of how PDF extraction broke lines."""
    return re.compile(r"\s+".join(re.escape(w) for w in s.split()))

def apply_edit(text: str, original: str, planted: str):
    hits = list(span_pattern(original).finditer(text))
    assert len(hits) == 1, f"original span matches {len(hits)} times: {original[:60]!r}"
    m = hits[0]
    orig_exact = m.group(0)
    seps = re.findall(r"\s+", orig_exact)            # keep the original line breaks where word slots line up
    words = planted.split()
    planted_exact = words[0] + "".join((seps[i] if i < len(seps) else " ") + w for i, w in enumerate(words[1:]))
    new = text[:m.start()] + planted_exact + text[m.end():]
    page = text[:m.start()].count("[p. ")
    return new, orig_exact, planted_exact, page

def main():
    edits = json.load(open(D / "edits.json"))
    papers = sorted({e["paper_id"] for e in edits})
    rng = random.Random(7)
    manifest = []
    for n, pid in enumerate(papers, 1):
        text = (D / "text" / f"{pid}.txt").read_text()
        letters = ["a", "b", "c"]; rng.shuffle(letters)
        clean_id = f"P{n:02d}-{letters[0]}"
        (VAR / f"{clean_id}.txt").write_text(text)
        twins = []
        for e, L in zip([e for e in edits if e["paper_id"] == pid], letters[1:]):
            vid = f"P{n:02d}-{L}"
            new, orig_exact, planted_exact, page = apply_edit(text, e["original_span"], e["planted_span"])
            # self-checks: one changed region, planted text present once in variant and absent from clean
            assert new.count(planted_exact) == 1 and planted_exact not in text, vid
            assert len(span_pattern(e["planted_span"]).findall(text)) == 0, vid
            (VAR / f"{vid}.txt").write_text(new)
            twins.append(vid)
            manifest.append({"variant_id": vid, "paper_id": pid, "kind": "planted", "type": e["type"], "page": page,
                             "original_span": orig_exact, "planted_span": planted_exact,
                             "evidence_quote": e["evidence_quote"], "evidence_page": e["evidence_page"],
                             "detection": e["detection"], "why_it_matters": e["why_it_matters"], "clean_twin": clean_id})
        manifest.append({"variant_id": clean_id, "paper_id": pid, "kind": "clean", "planted_twins": twins})
    (D / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    print(len(papers), "papers,", sum(m["kind"] == "planted" for m in manifest), "planted variants; all edits applied exactly once")

if __name__ == "__main__":
    main()
