"""Build the Unjournal test set: paper texts, curated human issues, and the GPT-5.2 Pro baseline issues.

Inputs come from the cloned llm-uj-research-eval repo (data/raw). Paper texts go to
data/papers (git-ignored); derived JSON goes to data/derived.
"""
import json, re
from pathlib import Path
import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/llm-uj-research-eval"
OUT = ROOT / "data/derived"; OUT.mkdir(parents=True, exist_ok=True)
PAPERS = ROOT / "data/papers"; PAPERS.mkdir(parents=True, exist_ok=True)

def pdf_text(pdf: Path) -> str:
    doc = fitz.open(pdf)
    return "\n".join(f"\n[p. {i+1}]\n" + page.get_text() for i, page in enumerate(doc))

def split_human(coda: str):
    """Split the curated critique into issues, keeping the severity heading each sits under."""
    sev, issues = "unspecified", []
    for line in coda.splitlines():
        s = line.strip()
        if not s:
            continue
        low = s.lower().rstrip(":")
        if low in {"necessary", "optional but important", "unsure", "optional", "important", "minor"} or (len(s) < 40 and not s.endswith(".") and ":" not in s and not s.startswith(("“", '"', "E1", "E2", "DR"))):
            sev = low
            continue
        if issues and (s.startswith(("E1", "E2", "DR", "“", '"')) and not re.match(r"^[A-Z][^:]{3,80}:", s)):
            issues[-1]["text"] += "\n" + s   # continuation (quote or commentary) of the previous issue
        else:
            issues.append({"severity": sev, "text": s})
    return issues

def main():
    comp = json.load(open(RAW / "results/key_issues_comparison.json"))
    matched = json.load(open(RAW / "results/key_issues_matched.json"))
    gold, base = {}, {}
    for x in comp:
        pid = x["gpt_paper"]
        txt = pdf_text(RAW / "papers" / f"{pid}.pdf")
        (PAPERS / f"{pid}.txt").write_text(txt)
        hi = matched.get(pid, {}).get("human_issues") or split_human(x["coda_critique"])
        gold[pid] = {"title": x["coda_title"], "human_issues": [{"id": f"H{i+1}", **h} for i, h in enumerate(hi)],
                     "coda_critique": x["coda_critique"], "n_chars": len(txt)}
        base[pid] = [{"id": f"B{i+1}", "claim": t} for i, t in enumerate(x["gpt_key_issues"])]
        print(pid, len(txt), "chars,", len(hi), "human issues,", len(base[pid]), "baseline issues")
    (OUT / "uj_gold_issues.json").write_text(json.dumps(gold, indent=1, ensure_ascii=False))
    (OUT / "uj_baseline_gpt52pro_issues.json").write_text(json.dumps(base, indent=1, ensure_ascii=False))

if __name__ == "__main__":
    main()
