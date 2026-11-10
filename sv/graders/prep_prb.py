"""Convert the PeerReview Bench parquet files we use into JSON (no pyarrow at runtime).

Run once: uv run --with pyarrow python -m sv.graders.prep_prb
Reads data/raw/peerreview-bench/{meta_reviewer,similarity_check}/*.parquet and writes
data/raw/peerreview-bench/json/{meta_reviewer,similarity_check}.json (git-ignored).
"""
import json
from pathlib import Path
import pandas as pd

D = Path(__file__).resolve().parents[2] / "data" / "raw" / "peerreview-bench"

def main():
    out = D / "json"; out.mkdir(exist_ok=True)
    m = pd.read_parquet(D / "meta_reviewer" / "eval-00000-of-00001.parquet").drop(columns=["file_refs"])
    papers = {int(p): g.paper_content.iloc[0] for p, g in m.groupby("paper_id")}
    items = m.drop(columns=["paper_content"]).astype(object).where(m.drop(columns=["paper_content"]).notna(), None)
    json.dump({"papers": {str(k): v for k, v in papers.items()}, "items": items.to_dict("records")},
              open(out / "meta_reviewer.json", "w"), default=int)
    s = pd.read_parquet(D / "similarity_check" / "eval-00000-of-00001.parquet")
    sp = {str(int(p)): g.paper_content.iloc[0] for p, g in s.groupby("paper_id")}
    pairs = s.drop(columns=["paper_content"]).astype(object)
    json.dump({"papers": sp, "pairs": pairs.to_dict("records")}, open(out / "similarity_check.json", "w"), default=int)
    print(len(items), "items,", len(papers), "papers;", len(pairs), "pairs,", len(sp), "papers")

if __name__ == "__main__":
    main()
