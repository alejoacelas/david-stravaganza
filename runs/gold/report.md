# Gold workstream report

## 1. Expanded human reference set (`data/derived/uj_human_items.json`)

Built by `uv run python -m sv.gold.extract_human`. 434 atomic criticisms from 27 evaluator
reports. Each item has evaluator id, a one-sentence criticism, a verbatim quote from the
report, whether the manager summary endorses it (with a verbatim quote), the author-response
label (conceded / rebutted / not addressed, with a verbatim quote), and matched curated issue ids.

Method: one Opus call per evaluator report splits it into atomic criticisms (Kim et al. style).
One Opus call per paper labels manager endorsement, author stance and curated-issue match.
**Curated-issue matching is a model call**, not word overlap.

### File mapping (`sv/gold/sources.py`)

Mapped by hand from each file's `title:` front matter. `UJ_map.csv` maps author-year to title
only, so it does not reach file names. Every paper mapped. Gaps:

- **Benabou et al. 2023**: Evaluation 2 (Treich) `eval2moralbhvr.md` is a stub that holds only
  the landing-page abstract. Both curated issues come from Treich, so 0/2 are covered.
- **Clancy 2024**: Evaluation 1 `e1technologicalrisks.md` is a stub. No manager summary file
  exists, so `manager_endorses` is null for all 30 items.
- **Clancy E2** (`e2technologicalrisks.md`): its parameter table was written one letter per row.
  It is rebuilt without spaces, so one quote from it verifies only with spaces ignored.
- **Peterman et al. 2025**: the single curated issue (ASQ validation in India, MHT across child
  development indices) describes the Weaver et al. paper (maternal cash transfers, India). It
  appears to be misassigned in the source curated list, so it has no match.
- **Williams et al. 2024**: H2, H4, H6 and H7 are attributed to "[Cloud]", who is not one of
  the two evaluators in the files. 6/8 are covered.
- Author responses exist for only 5 papers: Benabou, Bruers, Clancy, Green and McGuire.

| Paper | Evaluators used | Items | Manager endorses | Author: conceded / rebutted / not addressed | Items matched to curated | Curated issues covered |
|---|---|---|---|---|---|---|
| Acemoglu_et_al._2024 | E1, E2 | 19 | 11 | no response | 6 | 2/2 |
| Adena_and_Hager_2024 | E1, E2 | 34 | 19 | no response | 25 | 1/1 |
| Benabou_et_al._2023 | E1 | 8 | 1 | 2 / 6 / 0 | 0 | 0/2 |
| Bilal_and_Kaenzig_2024 | E1, E2 | 21 | 3 | no response | 5 | 3/3 |
| Blimpo_and_Castaneda-Dower_2025 | E1, E2 | 25 | 15 | no response | 6 | 3/3 |
| Bruers_2021 | E1, E2 | 25 | 12 | 16 / 1 / 8 | 2 | 1/1 |
| Clancy_2024 | E2, E3 | 30 | n/a (no summary) | 12 / 5 / 13 | 19 | 3/3 |
| Dullaghan_and_Zhang_2022 | E1, E2 | 37 | 16 | no response | 11 | 6/6 |
| Frech_et_al._2023 | E1, E2 | 25 | 11 | no response | 10 | 2/2 |
| Green_et_al._2025 | E1, E2 | 38 | 21 | 0 / 18 / 20 | 17 | 2/2 |
| McGuire_et_al._2024 | E1, E2 | 57 | 15 | 21 / 24 / 12 | 17 | 4/4 |
| Peterman_et_al._2025 | E1, E2 | 39 | 15 | no response | 0 | 0/1 |
| Weaver_et_al._2025 | E1, E2 | 50 | 19 | no response | 9 | 5/5 |
| Williams_et_al._2024 | E1, E2 | 26 | 19 | no response | 16 | 6/8 |

Curated issues covered: 39/43 (the 4 gaps are explained above). Some curated "issues" bundle
several criticisms; Adena's single H1 covers about six. As a result, curated-match counts per
item are high for those papers.

### Extraction checks

- **Quote verification** (mechanical substring check after whitespace, markdown-escape and
  quote-mark normalization): evaluator quotes 433/434 exact, plus 1 that matches once spaces
  are ignored (the Clancy E2 vertical table). Manager quotes 177/177. Author-response quotes 105/105.
  2 model-proposed curated ids that did not exist (e.g. "E1") were dropped and recorded in
  `curated_ids_dropped`.
- **Manual spot check**: I read 20 random items against their sources.
  - Quotes: 20/20 are verbatim and on point. One supports its criticism only weakly
    (Dullaghan E2-3: the quote does not name the specific cost-reduction methods).
  - Criticism faithful to the report: 19/20. McGuire E1-13 turns a reviewer's question
    ("Do you apply any exclusion criteria…?") into an assertion.
  - Manager endorsement: 19/20 plausible. Adena E1-1 counts the summary reproducing the
    evaluator's own comment as manager endorsement. Read `manager_endorses` as
    "the summary raises it", not strictly "the manager agrees".
  - Author labels: 5/6 plausible. McGuire E1-13 "rebutted" is arguably "addressed".
    Bruers E1-3 "conceded" is a partial concession.

## 2. G1 evidence checker (`sv/gold/g1_evidence.py`)

`check(paper_text, item)` returns, for each quote: `found`, `score`, `numbers_ok`,
`word_edits`, `page_found`, `page_claimed`, `page_claimed_ok`.

How it decides:
- **Normalization:** NFKC (expands ligatures), unified quote marks and dashes, line-end
  hyphenation joined, other hyphens dropped, `[p. N]` markers removed, whitespace collapsed,
  lowercase.
- **Locating the quote:** an exact substring hit scores 100. Otherwise it takes the best
  rapidfuzz `partial_ratio` window, then word-aligns the quote to that window.
- **Found rule:** the quote counts as found only if there are no whole-word differences.
  In-word character noise is tolerated (rapidfuzz ratio ≥ 80 per replaced block). Any digit
  difference rejects the quote. Paper-only footnote digits are ignored.
- **Ellipses:** a quote with an ellipsis is split, and each fragment must match.
- **Pages:** among duplicate exact hits, the one on the claimed page is preferred.

Calibration (`uv run python -m sv.gold.g1_calibrate`; cases in
`data/derived/g1_calibration.json`): 1118 cases from the 14 papers.
- 419 true quotes: 308 prose, 111 table-like; 8–40 words.
- 140 true quotes with 1–3 OCR-style character errors.
- 70 true quotes with a wrong claimed page.
- 489 fakes:
  - 112 with one number changed;
  - 126 with one or two words replaced or two words transposed;
  - 84 spliced from two places;
  - 167 Haiku paraphrases (light: 2–4 words changed; full).

Papers are split 7/7. The threshold was chosen on the first half by balanced accuracy over
score 70–100 and 0–1 word edits.

- **Chosen rule:** score ≥ 70 and 0 word edits. The score floor does not bind; the word-edit
  rule does the work.
- **Held-out (7 papers, 525 cases): precision 0.996, recall 0.932** (TP 261, FP 1, FN 19, TN 244).
  - Clean true quotes (prose and table) are found 100% of the time.
  - Every fake type is rejected 100% of the time, except full paraphrase (1/42 accepted).
    On inspection, that one differs from the true span only by commas.
- **OCR variants: 73% found** (all 140: 99 found). Of the 41 misses, 30 are rejected on
  purpose because the noise changed a digit (l↔1, O↔0). The rest are short words with a
  2-character slip (randorn/random, thc/the).
  - This is a trade-off: loosening the rule would admit one-word misquotes, which score
    in the same range (88–97).
  - It matters only when quotes come from a different text extraction than `data/papers`.
- **Baseline** for comparison: `partial_ratio` alone does best at threshold 100 (exact match
  only), with recall 0.746. One-word swaps and number changes score 88–99, so no lower
  threshold separates them from OCR noise.
- **Pages:** `page_claimed_ok` is true for 100% of found held-out true quotes with the right
  page, and for 0% with a wrong page.
- **Real reviewer output:** applied to the current R1/R2 reviews in `runs/reviews/`, all 238
  quotes are found. 237/238 claimed pages are correct.

## Spend

$16.46 of the shared ledger: extraction $8.94, labeling $7.38, Haiku paraphrases $0.14.
