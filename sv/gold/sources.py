"""Map the 14 test papers to their Unjournal evaluation files and load cleaned text.

Mapping was made by hand from the files' `title:` front matter (UJ_map.csv only
maps author-year to paper title, not to file names). Files that are only a
stub (title and abstract of the paper, no report text) are listed under STUBS.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVALS = ROOT / "data/raw/llm-uj-research-eval/data/unjournal_evaluations"

# paper id -> {"evaluators": {evaluator id: file}, "summary": file|None, "response": file|None}
MAP = {
    "Acemoglu_et_al._2024": {"evaluators": {"E1": "e1demandfordemocracy", "E2": "e2demandfordemocracy"},
                             "summary": "evalsumdemandfordemocracy", "response": None},
    "Adena_and_Hager_2024": {"evaluators": {"E1": "e1fundraisingcharitablegivingcapitan", "E2": "e2fundraisingcharitablegivingreiley"},
                             "summary": "evalsumfundraisingcharitablegiving", "response": None},
    "Benabou_et_al._2023": {"evaluators": {"E1": "eval1moralbhvr", "E2": "eval2moralbhvr"},
                            "summary": "evalsummoralbhvr", "response": "2k4ycf19"},
    "Bilal_and_Kaenzig_2024": {"evaluators": {"E1": "e1macroclimatechange", "E2": "e2macroclimatechange"},
                               "summary": "evalsummacroclimatechange", "response": None},
    "Blimpo_and_Castaneda-Dower_2025": {"evaluators": {"E1": "e1civicasymmetry", "E2": "e2civicasymmetry"},
                                        "summary": "evalsumcivicasymmetry", "response": None},
    "Bruers_2021": {"evaluators": {"E1": "e1animalwelfarecost", "E2": "e2animalwelfarecost"},
                    "summary": "evalsumanimalwelfarecost", "response": "responseanimalwelfarecost"},
    "Clancy_2024": {"evaluators": {"E1": "e1technologicalrisks", "E2": "e2technologicalrisks", "E3": "e3technologicalrisks"},
                    "summary": None, "response": "ar_returnstoscience"},
    "Dullaghan_and_Zhang_2022": {"evaluators": {"E1": "e1limitedmeatprod", "E2": "e2limitedmeatprod"},
                                 "summary": "evalsumlimitedmeadprod", "response": None},
    "Frech_et_al._2023": {"evaluators": {"E1": "e1pharmpricing", "E2": "e2pharmpricing"},
                          "summary": "evalsumpharmpricing", "response": None},
    "Green_et_al._2025": {"evaluators": {"E1": "e1reducingconsumption", "E2": "e2reducingconsumption"},
                          "summary": "evalsumreducingconsumption", "response": "authorsresponseunjournalevaluations22"},
    "McGuire_et_al._2024": {"evaluators": {"E1": "e1strongminds", "E2": "e2strongminds"},
                            "summary": "evalsumstrongminds", "response": "authorsresponsestrongminds"},
    "Peterman_et_al._2025": {"evaluators": {"E1": "e1safetynets", "E2": "e2safetynets"},
                             "summary": "evalsumsafetynets", "response": None},
    "Weaver_et_al._2025": {"evaluators": {"E1": "e1maternalcashtransfers", "E2": "e2maternalcashtransfers"},
                           "summary": "evalsummaternalcashtransfers", "response": None},
    "Williams_et_al._2024": {"evaluators": {"E1": "e1naturalregeneration", "E2": "e2naturalregeneration"},
                             "summary": "evalsumnaturalregeneration", "response": None},
}
# Files that hold only the paper's title/abstract scraped from a landing page, not the report.
STUBS = {"e1technologicalrisks", "eval2moralbhvr"}


def _grid_block(rows: list[str]) -> list[str]:
    """Rebuild one row of a pandoc grid table: join each column's fragments into a cell."""
    cols: dict[int, list[str]] = {}
    widths: dict[int, int] = {}
    for r in rows:
        parts = r.strip().strip("|").split("|")
        for i, p in enumerate(parts):
            widths[i] = max(widths.get(i, 0), len(p))
            if p.strip():
                cols.setdefault(i, []).append(p.strip())
    cells = []
    for i in sorted(cols):
        sep = "" if widths[i] <= 3 else " "   # one-letter-wide columns hold text written vertically
        cells.append(sep.join(cols[i]))
    return [" | ".join(cells)] if cells else []


def clean(md: str) -> str:
    """Drop YAML front matter; flatten pandoc grid tables into one line per table row."""
    md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)
    out, block = [], []
    for line in md.splitlines():
        s = line.strip()
        if re.fullmatch(r"\+[-=:+]+\+", s):          # grid border: flush the row above it
            out += _grid_block(block); block = []
            continue
        if s.startswith("|") and s.endswith("|"):
            block.append(s)
            continue
        if block:
            out += _grid_block(block); block = []
        out.append(line.rstrip())
    out += _grid_block(block)
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text)


def load(name: str | None) -> str | None:
    if not name:
        return None
    return clean((EVALS / f"{name}.md").read_text(errors="replace"))


def norm(s: str) -> str:
    """Normalization used for verifying quotes against markdown sources."""
    s = s.replace("\\", "")
    s = re.sub(r"[*_`#>]", "", s)
    s = re.sub(r"\[\^\d+\]", "", s)
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'").replace("–", "-").replace("—", "-")
    s = s.replace("…", "...")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def verify(quote: str, source: str) -> str | None:
    """'exact' if the normalized quote is in the normalized source, 'nospace' if it matches only
    once all whitespace is removed (source tables written vertically lose their spaces), else None."""
    if not quote or len(norm(quote)) < 8:
        return None
    q, src = norm(quote), norm(source)
    if q in src:
        return "exact"
    if q.replace(" ", "") in src.replace(" ", ""):
        return "nospace"
    return None
