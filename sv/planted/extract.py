"""Extract page-marked text for candidate planted-error papers (same format as sv/prep_unjournal.py)."""
import sys
from pathlib import Path
from sv.prep_unjournal import pdf_text, RAW

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data/planted/text"; OUT.mkdir(parents=True, exist_ok=True)

for pid in sys.argv[1:]:
    t = pdf_text(RAW / "papers" / f"{pid}.pdf")
    (OUT / f"{pid}.txt").write_text(t)
    print(pid, len(t), t.count("[p. "), "pages", t.count("Table"), "Table mentions")
