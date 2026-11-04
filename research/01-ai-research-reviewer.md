# Idea 1: Auditable AI research reviewer

Researched 3 November 2026.

## Conclusion

Worth building, but as an extension of existing pieces rather than a new reviewer. A general "AI reads a paper and critiques it" tool is now common and good. King and Worthington (Oct 2026) report that editors preferred Claude reviews over paid human reviews in 26 of 30 blind judgments. Refine sells this for $36–60 a paper. David's own study shows a one-shot GPT-5 Pro already covers about 80% of the issues human evaluators agreed on.

Two things are still missing, and David is well placed to supply both:

1. **Criticisms tied to checkable evidence.** That means a quoted passage, a rerun code output, or a reference lookup for each one. Rerunning code is the weakest link in every tool and study found. AI-led teams reproduced 37% of results, against 94% for human teams.
2. **A blind test of whether the AI finds valid, consequential problems that expert evaluators missed.** Nobody has published this for economics. David's 58 public evaluation packages with author responses are a rare test set for it.

The build should be a thin harness: an agent working in a container, deterministic checkers, a reference lookup and an evidence-linked output format. Most of the work goes into the blind judging protocol, not the reviewer.

The two biggest risks:

- **Many evaluated papers have no public code matching the version evaluators saw.** Of the 58 evaluated papers, 31 are still listed as unpublished working papers. Checking this sample comes first.
- **Separating The Unjournal from personal work.** The existing work is an Unjournal project with a co-PI (Valentin Klotzbücher) and a grant application to Coefficient Giving. This idea therefore belongs on the Unjournal side, not among David's personal projects.

## What David already has

- **Just Ask the Model** ([site](https://llm-uj-research-eval.netlify.app/), [repo](https://github.com/valentinklotzbuecher/llm-uj-research-eval), last pushed 23 Oct 2026). GPT-5 Pro gets each paper's PDF and a fixed rubric in a single prompt, with no agent loop and no retrieval. It covers 60 papers, 47 of them matched to human evaluations. Ratings show positive rank agreement with the human panel. In a critique-overlap analysis of 12 paper–evaluation pairs, judged by GPT-5.2 Pro, the model found about 80% of the issues human evaluators agreed on, and about 52% of the model's own issues matched a human concern. The study does not rerun code, check references or verify individual errors.
- **Concordance site** ([link](https://llm-uj-concordance-judgments.netlify.app/)). This is the archived judgment of human-versus-model issue overlap: 14 papers, 74.9% coverage of human issues. The page says the judgments come from a model judge and are not ground truth. A human annotation interface is linked, but the page does not show it being used.
- **Headless Codex pilot** ([page](https://llm-uj-research-eval.netlify.app/headless_codex_pilot)). Codex with gpt-5.5 ran on one paper (Bruers 2021) from extracted text cut off at 60,000 characters. No code reruns or reference checks. It is the nearest thing to an agentic reviewer so far.
- **Grant proposal** ([page](https://llm-uj-research-eval-project.netlify.app/proposal.html)). This is the Coefficient Giving application under its "AI for Forecasting and Sound Reasoning" call. David and Klotzbücher are co-PIs, with a $335k medium scenario. It already plans human adjudication of false-positive critiques. It names Casey Wimsatt of the Black Spatula Project as an advisor and mentions talks with Ben Golub about benchmarking Refine. A note from 23 Oct 2026 says King and Worthington weaken the novelty of comparing AI with human reviewers. It says the remaining contribution is "independent adjudication of critique validity and importance", which is exactly this milestone.
- **Public data** ([unjournal/unjournaldata](https://github.com/unjournal/unjournaldata)). `data/research.csv` lists 58 papers with published evaluations. Of these, 31 are unpublished working papers, 7 appeared in roughly top journals, 4 in decent journals and 5 are revise-and-resubmit. Most are in global health, development or the environment. The evaluation packages and author responses are on [PubPub](https://unjournal.pubpub.org/).
- Nothing in David's GitHub ([daaronr](https://github.com/daaronr)) or the Unjournal GitHub ([unjournal](https://github.com/unjournal)) reruns code or checks references. `daaronr/llm-paper-mirror` is archived and points to the repo above.

## Existing tools and evidence

Each claim below has been checked against the cited page unless marked otherwise.

**Full-paper AI reviewers**

- **Refine** ([refine.ink](https://www.refine.ink/), [pricing](https://www.refine.ink/pricing)). A closed, hosted product from Refine Technologies, cofounded by economist Ben Golub ([Wikipedia](https://en.wikipedia.org/wiki/Benjamin_Golub)). It checks reasoning, numbers, consistency between text and tables, and code, and ties each issue to a passage. It costs $59.99 per review, or $36 each in a pack of 10. Its only evidence is the company's own benchmark: it won 197 of 215 head-to-head comparisons against other models. The site says it checks "code" but does not say it executes code. A third-party review says its FAQ excludes fact-checking of citations ([Manusights](https://manusights.com/blog/is-refine-worth-it), a competitor; not verified against Refine's FAQ). The strongest commercial option, and a natural comparison arm for the test.
- **Stanford Agentic Reviewer** ([paperreview.ai](https://paperreview.ai/), [tech overview](https://paperreview.ai/tech-overview)). Free and closed. It reads only the first 15 pages and is aimed at machine-learning venues. On 147 ICLR 2025 papers, its scores correlated with one human reviewer at 0.42 (Spearman), against 0.41 between two humans. It was not built for economics or for finding errors.
- **Sakana AI Scientist reviewer** ([paper](https://arxiv.org/html/2408.06292), [repo](https://github.com/SakanaAI/AI-Scientist), about 15k stars, last pushed Dec 2025). Open source. On predicting ICLR 2022 accept/reject decisions, it reached balanced accuracy of 0.65, against 0.66 for humans. Its false-positive rate was 0.31, against 0.17 for humans. A review costs $0.25–0.50. It predicts decisions and does not verify errors.
- **q.e.d Science** ([bioRxiv announcement](https://connect.biorxiv.org/news/2025/11/04/qed_review_tool), [The Scientist](https://www.the-scientist.com/can-ai-tools-spot-great-science-before-reviewers-do-74677)). Closed. It builds a tree of each paper's claims and finds gaps in the support for them. It runs as a pilot for bioRxiv authors and has scored 57,455 preprints. Its scores correlate positively with the rank of the journal that later published each paper. Built for biology; pricing not checked.
- **ICLR 2025 Review Feedback Agent** ([ICLR blog](https://blog.iclr.cc/2025/04/15/leveraging-llm-feedback-to-enhance-review-quality/), [arXiv 2504.09737](https://arxiv.org/abs/2504.09737v1), [repo](https://github.com/zou-group/review_feedback_agent)). Open source and built on Claude Sonnet 3.5. It critiques reviews, not papers. A randomized trial covered about 19k treated reviews. In blind preference tests, the feedback improved reviews in 89% of cases, and about a quarter of treated reviewers updated their reviews. It shows how to use reliability guardrails, not how to find errors.
- **AAAI-26 AI review pilot** ([arXiv 2604.13940](https://arxiv.org/pdf/2604.13940)). Every main-track submission, reportedly 22,977, received one labelled AI review, and surveyed authors and committee members preferred the AI reviews on technical accuracy. The figure of under $1 per paper comes from secondary coverage and is unverified.
- **King and Worthington (2026)**, "AI Article Reviews Dominate Human Peer Reviews at Their Best" ([PDF](https://gking.harvard.edu/files/peerless.pdf), [Marginal Revolution](https://marginalrevolution.com/marginalrevolution/2026/10/ai-dominates-human-peer-reviews.html)). A study, not a tool. Claude Opus 4.8 reviewed 124 social-science submissions. A blind audit found claims contradicted by the manuscript in 5.5% of AI claim assessments, against 15.9% for human ones. Figures are taken from David's own summary of the paper and from secondary coverage; I confirmed the PDF exists but did not read it.

**Error detection and verification**

- **Black Spatula Project** ([site](https://the-black-spatula-project.github.io/), [GitHub](https://github.com/The-Black-Spatula-Project)). An open volunteer project testing whether language models can find errors in papers. It collects prompts, a spreadsheet of arXiv papers with known errors, and volunteer expert checkers. It publishes no accuracy numbers. Its repos are small (19 stars) and were last updated Aug–Oct 2026. Useful mainly as a community and a source of prompts.
- **SPOT benchmark** ([arXiv 2505.11855](https://arxiv.org/abs/2505.11855v1)). 83 published papers with 91 errors serious enough to lead to an erratum or retraction. The best model, o3, recovered 21.1% of the errors, and only 6.1% of its flags were real errors. Repeated runs rarely found the same errors. A later Google pipeline reports 89.7% recall on a 26-paper math/CS subset ([arXiv 2606.28277](https://arxiv.org/pdf/2606.28277)); this cannot be compared directly with the full benchmark. This is the most direct published evidence that most unaided AI error flags are false.
- **statcheck** ([repo](https://github.com/MicheleNuijten/statcheck), active Oct 2026) and **scrutiny** ([CRAN](https://CRAN.R-project.org/package=scrutiny)). Open-source deterministic checks. statcheck recomputes p-values from reported test statistics. scrutiny runs GRIM and GRIMMER checks, which test whether reported means and standard deviations are possible given the sample size. In a reanalysis of statcheck's validation data, only 60.4% of its flags were real inconsistencies, and it caught 51.8% of true inconsistencies ([Schmidt, arXiv 1610.01010](https://arxiv.org/pdf/1610.01010)). Both are cheap. They suit psychology-style reporting better than economics regression tables.
- **GPTZero Hallucination Check** ([ICLR 2026 report](https://gptzero.me/news/iclr-2026/)). Closed. Scanning 300 ICLR 2026 submissions, it found 50 with at least one fabricated citation, most of which reviewers missed. This is the company's own claim. Checking that references exist is easy to reproduce with Crossref and OpenAlex lookups. Checking that a cited source actually supports the claim is harder, and no tool found evaluates that.

**Rerunning code**

- **AI Data Editor workflow**, Schwartz, Andrews and Shapiro ([NBER w35782](https://www.nber.org/papers/w35782), Sept 2026; [GitHub org](https://github.com/MetaEconomics)). The closest existing system to the code part of this idea. The workflow takes an economics article's published replication package, reruns it, flags differences from the published results and runs sensitivity checks. It flagged discrepancies in 3,460 of 4,452 articles from five journals. The abstract reports no rate of confirmed errors or false positives, and the high flag rate suggests many flags are minor. The code is not out yet: the README of `MetaEconomics/AIDataEditorWorkflowPublic` says "Public release in preparation." Watch for it and reuse it if it appears.
- **Institute for Replication (I4R) human vs AI teams** ([I4R DP 195](https://econpapers.repec.org/paper/zbwi4rdps/195.htm); later published in PNAS as "AI-assisted teams outperform AI-led teams but not human-only teams", [manuscript](https://repository.essex.ac.uk/43026/1/pnas_2025-24747RR_Manuscript_File.pdf)). 103 teams were randomly assigned to work without AI, with AI assistance or with AI in charge. Results were reproduced by 94% of human-only teams, 91% of AI-assisted teams and 37% of AI-led teams. Human teams found more major errors than either AI condition. This used ChatGPT in 2024–25; current agents are likely better, but I found no published update. I4R has Open Philanthropy funding for further games on language-model replication ([Good Ventures](https://www.goodventures.org/?p=4370)); I found no 2026 results.
- **REPRO-Bench** ([arXiv 2507.18901](https://arxiv.org/abs/2507.18901v1)) and **CORE-Bench**. Agents get a social-science paper and its replication package and score its reproducibility. The best agent at publication scored 36.6% accuracy on a four-level scale. On the [authors' blog](https://ddkang.substack.com/p/claude-45-opus-solves-core-bench), CORE-Bench is now solved, but REPRO-Bench, the social-science version, is not. This is a ready-made benchmark for the code-rerun component.

## Scores against David's criteria

A = needs only public material, B = first version testable, C = real payoff, D = keeps The Unjournal and personal work separate, E = cheap, static, little upkeep. Each is scored from 1 (bad) to 3 (good).

For existing tools, A–E means: how well this tool would serve as David's build or as a component of it.

| Option | A | B | C | D | E | Note |
|---|---|---|---|---|---|---|
| David's proposed reviewer | 3 | 2 | 3 | 2 | 2 | A: papers, packages and author responses are public. B: testable, but only if 10 papers have usable code and blind expert judges can be found. C: no published answer yet to "does AI find what experts missed?" in economics. D: inherently an Unjournal project; fine if housed and funded there. E: results are static pages; each run costs API money and compute time, done in batches, not weekly. |
| Just Ask the Model (existing) | 3 | 3 | 2 | 2 | 3 | Already built and public. Does not rerun or verify anything, so it cannot answer the milestone question by itself. Same Unjournal ownership. |
| Refine | 3 | 3 | 2 | 3 | 2 | Run it on public PDFs as a comparison arm. Closed, so its criticisms cannot be traced to their evidence beyond the quoted passage. $360 for 10 papers. |
| Stanford Agentic Reviewer | 3 | 3 | 1 | 3 | 3 | Free, but it reads only 15 pages and is tuned for ML conferences. A weak comparison arm. |
| Sakana AI Scientist reviewer | 3 | 2 | 1 | 3 | 3 | Open source and cheap, but it predicts accept/reject decisions and does not find errors. |
| q.e.d Science | 3 | 2 | 2 | 3 | 2 | Claim-tree method worth borrowing. Biology focus; access for economics papers unverified. |
| Black Spatula Project | 3 | 1 | 2 | 3 | 3 | Prompts and volunteers, no system or accuracy data. Already linked through Casey Wimsatt. |
| AI Data Editor workflow (NBER) | 3 | 2 | 3 | 3 | 2 | The best code-rerun component for economics if released. Not yet public; unvalidated flag rate. |
| statcheck / scrutiny | 3 | 3 | 1 | 3 | 3 | Cheap deterministic checks to include. Rarely fire on economics papers. |
| GPTZero Hallucination Check | 3 | 3 | 1 | 3 | 2 | Checks that references exist; easy to replicate with Crossref and OpenAlex. Fabricated citations are unlikely in evaluated economics papers. |
| REPRO-Bench | 3 | 3 | 2 | 3 | 3 | Not a reviewer. Use it to test the code-rerun component before spending expert time. |

## What progress looks like

### Steps to the first milestone

1. **Check which papers are usable (about 1 week).** For each of the 58 published evaluations, record:
   - the paper version the evaluators saw (PubPub links it);
   - whether a public replication package exists for that version;
   - whether data access is restricted or Stata is required;
   - whether the authors published a response.

   Pick 10 papers: ideally at least 5 with runnable code, the rest for text and reference checks only. If fewer than 5 have runnable code, report it and split the milestone into a code part and a text part.
2. **Fix the test inputs.** Store hashes of the PDF, supplements and replication package for each paper. Write the judging protocol before any AI output exists, and preregister it on OSF. It should define:
   - **valid:** the problem is real;
   - **consequential:** it would change a main conclusion or a reader's confidence materially;
   - **missed:** no human evaluator raised it.

   Also set the pass threshold in advance. My suggestion: at least one valid, consequential, missed problem in 3 or more of the 10 papers, and at least half of the AI's top-5 problems per paper judged valid.
3. **Build the harness** (2–4 weeks). Run Claude Code or Codex headless in a container holding the paper, its supplements and its code. The reviewer outputs a fixed JSON format in which every problem must carry one kind of evidence:
   - a page-anchored quote;
   - a command plus its log and a comparison of numbers against the paper;
   - a reference lookup through Crossref or OpenAlex, with the passage the paper relies on.

   Problems without evidence are dropped automatically. statcheck and scrutiny run as tools inside the harness. Before spending expert time, test the code-rerun step on a slice of REPRO-Bench.
4. **Run the comparison arms**: the new reviewer, the existing one-shot GPT-5 Pro outputs from Just Ask the Model, and Refine (about $360).
5. **Judge blind.** Pool each paper's problems from the human evaluations and from every AI arm. Rewrite them into one neutral style so judges cannot tell the source. Have 2–3 independent economists rate each problem against the step 2 definitions. Use the published author responses as a second, cheaper signal of validity: authors who concede a point have effectively confirmed it. Recruit and pay judges through a public call, not The Unjournal's evaluator records, to stay within criterion A.
6. **Publish** a static site with one card per problem: the claim, its evidence, the judges' verdict and whether the human evaluators raised it. Add a short write-up of the results.

### One step past the milestone

Run the reviewer on papers as they first become public, and store the output with a timestamp and hash. When human evaluations of those papers are later published, compare them. This rules out the AI having seen the evaluations, a leakage risk the retrospective test cannot rule out, since the evaluations are on the web and newer models may have trained on them. It also produces the "impact tracker" module from David's shortlist cheaply: check later versions of each paper for which flagged problems the authors fixed. Use only papers whose evaluation is public by the time anything is published.

### Hardest technical risk

Getting a short list of flags that are mostly right. Every measured system produces mostly false or trivial flags:

- SPOT: 6.1% of o3's flags were real errors;
- statcheck: 60.4% of flags were real inconsistencies;
- AI Data Editor: discrepancies flagged in 78% of articles;
- AI Scientist reviewer: 0.31 false-positive rate, against 0.17 for humans.

Blind judges will judge on precision. Requiring evidence for each problem and running the code are the main defences. The secondary risk is practical: much of the code needed to rerun these papers may be missing, cover a later version of the paper, or depend on restricted data or a Stata licence.

### Build or extend

Extend:

- reuse the Just Ask the Model repo for its data, prompts and model-judge concordance code;
- reuse an off-the-shelf agent (Claude Code or Codex headless) as the reviewer instead of writing an agent loop;
- reuse statcheck, scrutiny, and Crossref and OpenAlex for the deterministic checks;
- adopt the NBER AI Data Editor workflow if it is released in time;
- buy Refine runs as a comparison arm.

Build only the evidence-linked output format, the container harness, the blind-judging packet and the static results site. The new contribution is the blind test, not the reviewer.

### Separation and money (criterion D)

This sits inside an existing Unjournal research program with a co-PI and a pending grant. It should live in the `unjournal` GitHub org or Klotzbücher's repo, with any API, judge or Refine spending paid by The Unjournal. It should not appear on David's personal projects hub as a personal project or link to his personal support routes. If David wants it personal instead, Klotzbücher has to agree, and the grant budget has to exclude it. That is a decision for David; I could not tell from public pages how far the grant has progressed.

## Unverified or uncertain

- Refine's claim to check "code": I could not tell whether it executes code.
- The q.e.d Science pricing, and whether it accepts economics papers.
- The AAAI-26 cost per paper.
- The code repository for the NBER AI Data Editor workflow (the public repo says the release is in preparation).
- How many of the 58 evaluated papers have usable public code. Not checked; this is step 1.
- King and Worthington's figures come from David's AI-generated summary and from press coverage. I did not read the PDF.
