"""Write runs/reviews_report.md: item counts, failures and cost per reviewer and set."""
import json
from collections import defaultdict
from pathlib import Path
from sv import llm
from sv.reviewers import prompts as P

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs" / "reviews"
ORDER = ["R0a", "R0b", "R1", "R1s0", "R1s1", "R1s2", "R2"]


def costs():
    c = defaultdict(float)
    for l in llm.LEDGER.read_text().splitlines():
        r = json.loads(l)
        if r["tag"].startswith("rev:"):
            _, rev, *_rest = r["tag"].split(":")
            key = f"R1s{r['tag'].rsplit(':s', 1)[1]}" if rev == "R1" else rev
            c[key] += r["usd"]
    return c


def main():
    c = costs()
    rows = []
    for rev in ORDER:
        for set_dir in sorted((OUT / rev).glob("*")) if (OUT / rev).exists() else []:
            files = [f for f in set_dir.glob("*.json") if not f.name.startswith("_")]
            counts = [len(json.loads(f.read_text())) for f in files]
            fails = json.loads((set_dir / "_failures.json").read_text()) if (set_dir / "_failures.json").exists() else []
            notes = [json.loads(m.read_text()).get("note") for m in (set_dir / "_meta").glob("*.json")]
            sev = defaultdict(int)
            for f in files:
                for it in json.loads(f.read_text()):
                    sev[it.get("severity")] += 1
            sev_s = ", ".join(f"s{k}:{v}" for k, v in sorted(sev.items(), key=lambda x: str(x[0])) if k)
            rows.append(f"| {rev} | {set_dir.name} | {len(files)} | {sum(counts)} | "
                        f"{min(counts, default=0)}-{max(counts, default=0)} | {sev_s or '-'} | {len(fails)} | "
                        f"{sum(1 for n in notes if n)} |")
    total = sum(c.values())
    md = f"""# Reviewer runs

Model: claude-opus-5-5, effort "high", input = paper text only, no tools. Code: `sv/reviewers/`.
Outputs: `runs/reviews/<reviewer>/<set>/<paper_id>.json`; raw replies and notes in `_meta/`.

| Reviewer | Set | Papers | Items | Per paper | By severity | Failures | Truncated |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

R1 is R1s0 under another name. R2 pools R1s0-R1s2, so its own cost is only the verifier call.

## Cost (ledger tags `rev:*`, conservative rates)

| Part | USD |
|---|---|
{chr(10).join(f"| {k} | {v:.2f} |" for k, v in sorted(c.items()))}
| **Total** | **{total:.2f}** |

## Prompts

R0b: {P.R0B_SOURCE}. Kept their role, debiasing and key-issues wording; dropped the
assessment summary and metrics keys. The paper goes in the user turn as page-marked text
(they attached the PDF).

System:
```
{P.R0B_SYSTEM}
```
User:
```
{P.R0B_USER}
```

R1 and the R2 verifier put the paper in a shared, prompt-cached system block:
```
{P.PAPER_SYSTEM}
```
R1 user turn:
```
{P.R1_USER}
```
R2 verifier user turn (items = the pooled R1s0-R1s2 items as JSON):
```
{P.VERIFY_USER}
```
"""
    (ROOT / "runs" / "reviews_report.md").write_text(md)
    print(md[:1500])


if __name__ == "__main__":
    main()
