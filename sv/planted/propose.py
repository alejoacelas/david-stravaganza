"""Ask Opus for candidate planted-error edits per paper. Candidates are only proposals:
each one is checked by hand against the paper before it goes into sv/planted/edits.py."""
import json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from sv import llm

ROOT = Path(__file__).resolve().parents[2]
TEXT = ROOT / "data/planted/text"
OUT = ROOT / "data/planted/candidates"; OUT.mkdir(parents=True, exist_ok=True)

PROMPT = """You are helping build a benchmark of planted errors in research papers. Below is the
page-marked text of an empirical paper ("[p. N]" marks the start of PDF page N).

Propose 8 candidate edits. Each edit changes ONE short span of the paper's running text (not a
table) so that it contains exactly one error that an expert reader could detect from the paper
itself. Use these types, at least one of each:
 a  a number in the text contradicts the table it cites (change the number in the text)
 b  the sign/direction of an effect in the text is reversed relative to the table
 c  significance overstated: text calls significant an estimate that the table shows insignificant (or misstates SE / stars)
 d  sample size in the text inconsistent with the sample size reported elsewhere (table N or another section)
 e  one inserted sentence drawing a conclusion the design cannot support (causal claim from correlational evidence, generalization beyond the sample) - append it after an existing sentence
 f  arithmetic error in a derived quantity stated in the text (percent change, ratio, cost-effectiveness) that can be recomputed from numbers given in the paper

Requirements:
- The error must touch a MAIN result (abstract, intro summary of results, or main results section), be unambiguous, and blend in stylistically.
- For a-d and f, the contradicting evidence must be present in the extracted text (quote it). Check that the table numbers you rely on are legible in the extracted text (tables may be garbled).
- original_span must be copied VERBATIM from the text (line breaks may be written as single spaces), 40-250 characters, and must occur exactly once in the paper. planted_span is the edited version of the same span.
- Prefer spans in the body text rather than the abstract, so the abstract does not contradict the error trivially, unless the error is in the abstract itself.

Return JSON only: a list of objects with keys
 type, page, original_span, planted_span, evidence_quote (verbatim text, e.g. table row, that shows the correct value), evidence_page, detection (what a correct detection must say), why_it_matters.

PAPER TEXT:
"""

def run(pid):
    txt = (TEXT / f"{pid}.txt").read_text()
    r = llm.call(PROMPT + txt, model=llm.OPUS, max_tokens=12000, tag=f"planted-propose:{pid}")
    (OUT / f"{pid}.json").write_text(json.dumps(llm.parse_json(r), indent=1, ensure_ascii=False))
    print(pid, "ok")

if __name__ == "__main__":
    with ThreadPoolExecutor(5) as ex:
        list(ex.map(run, sys.argv[1:]))
    print("spent", llm.spent())
