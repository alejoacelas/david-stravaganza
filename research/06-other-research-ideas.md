# Other candidate ideas: starting points, comparables, milestones

Checked 3 November 2026. Scores use David's criteria: A public material only, B testable first version, C real payoff, D Unjournal and personal projects kept apart (especially money), E cheap static hosting with no weekly attention. "Unverified" marks claims I did not confirm at the source.

## Ranking

1. **Self-checking impact directory.** Best fit. It is a personal project, all inputs are public, the gap is concrete and measurable, and it already has a weekly automated job to hang the checks on.
2. **Impact tracker.** Strong payoff for The Unjournal and fully public, but the hard part (did authors act on a suggestion?) is an unsolved research task. Best built as a module of the research reviewer, as David suggests.
3. **Forecast-to-decision workbench.** The model, the forecasts and Squiggle already exist. What is missing is a named decision and a decision-maker who wants it, and the outside builder can't supply either.
4. **Research-to-decision-maker matching.** Weakest for an outsider. Most of the matching already exists in the dashboard; the missing piece is the introduction, which needs David's people and time.

---

## 1. Impact tracker

**Conclusion:** worth building as a version watcher first, with "which suggestions were taken up" as a second step judged by humans. Automated uptake detection is not reliable yet.

**Starting point.** Evaluations and author responses are public on [unjournal.pubpub.org](https://unjournal.pubpub.org/). The public [unjournaldata](https://github.com/unjournal/unjournaldata) repo already has `bibliometrics.csv` (153 evaluated papers matched to OpenAlex, 89 with a journal of publication) and `bibliometrics_history.csv`. But that history has only two snapshots (17–18 January 2026) and nothing has refreshed since. It tracks citations and journal placement, not versions or content changes.

**Comparables (all verified to exist):**

| Tool | What it does | A | B | C | D | E |
|---|---|---|---|---|---|---|
| [OpenAlex locations](https://help.openalex.org/data/locations/) | Labels each copy of a work as submitted, accepted or published version | yes | yes | partial: tells you a new version exists, not what changed | n/a | free API |
| [Crossref retractions and updates](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) | Retraction Watch data in the REST API since Jan 2025; `update-to` field | yes | yes | narrow: only formal corrections and retractions | n/a | free |
| arXiv versions plus [comparxiv](https://pypi.org/project/comparxiv/) | latexdiff between arXiv versions | yes | yes | low for economics: most Unjournal papers are NBER/SSRN PDFs, not arXiv LaTeX | n/a | free, but beta and unmaintained since 2022 |
| [eLife reviewed preprints](https://elifesciences.org/inside-elife/e9d530fc) | Publishes reviews, author's list of changes, and an updated assessment per version; reports evidence rating improved for 44% of papers by version of record | yes | done by hand | high, but it relies on authors listing changes | n/a | staff time |
| [ARIES corpus](https://aclanthology.org/2024.acl-long.377) (ACL 2024) | Matches reviewer comments to the edits made in response, on OpenReview CS papers | yes | yes | shows the task is hard: models, GPT-4 included, did poorly at matching comments to edits | n/a | research dataset |
| Preprint-vs-published studies, e.g. [Carneiro et al. 2020](https://link.springer.com/10.1186/s41073-020-00101-3) | Compare bioRxiv preprints with journal versions; changes are mostly modest | yes | n/a | context: expect small changes | n/a | n/a |

**David's version:** A yes (published papers, evaluations, author responses). B yes for version detection. C real: it gives The Unjournal evidence of influence, which funders ask for. D fine if it stays an Unjournal tool. E fine: a scheduled GitHub Action writing static JSON.

**Progress.**
- *First milestone:* for every evaluated paper, a static page showing whether a newer version exists than the one evaluated (OpenAlex, NBER and SSRN dates, journal publication), with links. Test: a hand check of 20 papers agrees on "newer version exists" in at least 18.
- *One step past:* for 10 papers that have a newer version, extract each evaluator suggestion and label it addressed, partly addressed or not addressed, with the quoted passage as evidence. Score the labels against a blind human judge. ARIES suggests expecting modest agreement at first.

**Main risk:** uptake attribution. A changed paragraph does not prove the evaluation caused it (journal referees also asked for changes). Report "consistent with the suggestion", never "because of the evaluation".

---

## 2. Forecast-to-decision workbench

**Conclusion:** the modelling pieces exist and are good. The missing piece is a concrete decision with a threshold, and that has to come from a funder or company, not from the builder. Only worth it if David can name one decision first.

**Starting point.** The [cultured chicken cost model](https://unjournal.github.io/cm_pq_modeling/) is a Monte Carlo cost model (engine `2026-10-29.1`, default median about $17/kg of hybrid product, $213/kg dry cell mass). It already has a sensitivity chart (its own caveat: "a dollar-swing ranking, not a variance decomposition"), workshop beliefs, a Squiggle version on [Squiggle Hub](https://squigglehub.org/models/Unjournal-modelingPQs/cultured_meat_improved_by_squiggle_improve), and a cost-to-demand bridge to an adoption model (`dashboard/demand.qmd` in [the repo](https://github.com/unjournal/cm_pq_modeling)). The [Animal Futures update](https://uj-animal-futures-update.netlify.app/) summarises 21 Metaculus questions. It says itself that the useful next step is "to name the decision, threshold, and additional evidence that would change a course of action." Both are Unjournal projects.

**Comparables (all verified to exist):**

| Tool | What it does | A | B | C | D | E |
|---|---|---|---|---|---|---|
| [Squiggle](https://www.squiggle-language.com/) / Squiggle Hub | Probabilistic estimation language; public hosted models | yes | yes | already used here | n/a | free |
| [Guesstimate](https://www.getguesstimate.com/) | Spreadsheet-style Monte Carlo | yes | yes | low; superseded by Squiggle for this use | n/a | free |
| [Rethink Priorities CCM](https://ccm.rethinkpriorities.org/) | Ready-made cost-effectiveness models with adjustable assumptions, including animal welfare interventions | yes | yes | closest analogue: the user picks an intervention and assumptions and gets a comparison | n/a | hosted by RP |
| [Analytica](https://analytica.com/) | Influence diagrams, decisions and value of information | yes | yes | high in principle | n/a | paid desktop and cloud |
| [Metaculus conditional pairs](https://www.metaculus.com/questions/15205/introducing-conditional-pairs/) | P(A given B) and P(A given not B), embeddable | yes | yes | links a forecast to a lever | n/a | free |
| [GiveWell CEA uncertainty work](https://forum.effectivealtruism.org/posts/Nb2HnrqG4nkjCqmRg/quantifying-uncertainty-in-givewell-cost-effectiveness) (outside, in Squiggle) | Expected value of perfect information per parameter | yes | yes | the method to copy | n/a | n/a |
| Causal | Was a business modelling app; acquired by Lucanet in late 2024, standalone status unclear (unverified) | n/a | n/a | not relevant | n/a | n/a |

**David's version:** A yes. B only once a decision is named. C depends entirely on whether someone makes that decision differently. D fine (Unjournal). E fine: the model already runs client-side on GitHub Pages.

**Progress.**
- *First milestone:* pick one decision with a threshold, e.g. "a funder backs open-access growth-factor research if it moves P(hybrid cost < $X/kg by 2036) by more than Y". Add a decision panel that shows the probability of crossing the threshold, plus a per-parameter expected value of information ranking that replaces the dollar-swing chart. Test: the ranking reproduces under re-runs and a domain expert agrees the top three parameters are the ones worth researching.
- *One step past:* feed relevant Metaculus forecasts into the decision panel as inputs (e.g. state bans as a demand shifter), so a forecast change visibly moves the decision probability.

**Main risk:** no real decision-maker. Without one it becomes a nicer sensitivity chart. The model is also unvalidated by its own account, so value-of-information rankings could mostly reflect arbitrary prior ranges.

---

## 3. Research-to-decision-maker matching

**Conclusion:** least suited to an outside builder. Most of the paper-to-decision linking already exists in the dashboard. The missing step, introductions, needs David's relationships and ongoing attention, which breaks criterion E.

**Starting point.** The [prioritization dashboard](https://uj-prioritization-dashboard.netlify.app/) loads 1,878 papers from a public `data.js`. Of these, 360 have `org_relevance_tags` naming organizations (e.g. "UK AI Security Institute; EU AI Office; …"), and `crux_matches.js` links 575 papers to 1,039 cruxes from EA Forum problem profiles and 132 Pivotal Questions, each with a one-line reason. `impact/assessments.js` holds 154 completed assessments with a "decision counterfactual and VOI" field. The dashboard also routes into Unjournal's internal workflow (team forms, sign-in hub, "reward-eligible" route, a "Sponsor an evaluation" idea). An outside builder should stay on the public data files only.

**Comparables (all verified to exist):**

| Tool | What it does | A | B | C | D | E |
|---|---|---|---|---|---|---|
| [Overton](https://www.overton.io/) | 33M+ policy documents; finds where research is cited in policy; "Overton Engage" lists where policymakers ask for evidence | data is public, tool is paid (institutional pricing, no public price) | yes | high; the strongest comparable | n/a | paid |
| [Policy Commons](https://policycommons.net/) | Grey literature and think-tank reports | yes | yes | medium: a source of "who works on this" | n/a | free and paid tiers (unverified) |
| [J-PAL Policy Insights](https://www.povertyactionlab.org/policy-insights) | Staff-written evidence summaries by sector, linked to studies | yes | n/a | high, but driven by staff and relationships | n/a | staff time |
| [3ie Development Evidence Portal](https://developmentevidence.3ieimpact.org/) | Impact evaluations coded by intervention and outcome | yes | yes | medium: shows a taxonomy to borrow | n/a | free |
| [Apolitical](https://apolitical.co/) | Learning network for 500k+ public servants | n/a | n/a | it is a channel to decision-makers, not a matcher | n/a | n/a |
| [Elicit](https://elicit.com/), [Consensus](https://consensus.app/) | Search and summarise papers for a question | yes | yes | they answer "what does research say", not "who should hear about it" | n/a | paid tiers |

**David's version:** A yes if limited to the public data files. B partly: matches can be scored, outcomes slowly. C real only if introductions happen. D risk: it sits inside an Unjournal tool that has sponsorship and compensation ideas attached. E fails: introductions need recurring human work.

**Progress.**
- *First milestone:* for the 20 highest-priority evaluated papers, a public page listing named organizations, the specific decision each faces, and evidence (a policy document or public statement citing the topic, found via Policy Commons or the organization's own site). Test: two people who know the area rate each match as plausible and specific.
- *One step past:* add a citation watch (OpenAlex citing works plus Overton where available) that reports when a matched organization later cites the paper.

**Main risk:** it turns into a list of plausible names that nobody contacts. The value is in the introduction, which is the part that needs David.

---

## 4. Self-checking impact directory

**Conclusion:** the best fit of the four. It is personal (repo [daaronr/impact-directory](https://github.com/daaronr/impact-directory)), uses only public pages, and has a measurable problem today: none of its 3,045 claims has been rechecked since April.

**Starting point, from the live data file** (`/data/all_data.json`, 2 November 2026):
- 3,018 organizations, 3,046 offerings, 3,045 claims. Every claim has `updated` in April 2026 and `status: active`. All 12 sources show `last_crawled` 10–11 April 2026.
- A weekly GitHub Action (`scheduled-refresh.yml`) runs every Monday and succeeds. But the commits it makes since at least 19 October change one line, the `generated_at` date. The importers appear to fail or return nothing new, and the workflow tolerates that (`continue-on-error: true`). So the site says "Data last updated: 2026-11-02" while the claims are seven months old.
- No claim has its own source URL. Claims point to a source directory (e.g. Pledge 1%), not the page with the wording.
- 1,841 claims (60%) come from the Pledge 1% showcase and all share one template sentence ("We pledge 1% of equity, product, and employee time for social impact."). That conflicts with the repo's own rule that `claim_text` is the organization's exact wording.
- Claim types are pledges (1,909) and percentages (1,036). Nothing records reported or certified giving, so "pledged" and "actually gave" can't be told apart yet.

**Comparables (all verified to exist unless marked):**

| Tool | What it does | A | B | C | D | E |
|---|---|---|---|---|---|---|
| [changedetection.io](https://changedetection.io/) | Open-source page watcher (self-host free, hosted $8.99/month for 5,000 watches) | yes | yes | detects change, not meaning | yes | cheap |
| [Visualping](https://visualping.io/) | Hosted page watcher with AI "is this change important" | yes | yes | same, paid | yes | paid |
| Internet Archive Save Page Now (unverified, from memory) | Stores a dated snapshot as evidence | yes | yes | provides the "as of" evidence a claim needs | yes | free |
| [1% for the Planet](https://www.onepercentfortheplanet.org/faqs) | Certifies members' giving each year; only certified members may use the logo (per third-party pages; FAQ confirms it "certif[ies] donations") | yes | n/a | a ready source of *reported, certified* giving | yes | n/a |
| Pledge 1% showcase | Self-reported, no annual certification (per the directory's own importer notes) | yes | n/a | pledge only | yes | n/a |
| [Candid APIs](https://developer.candid.org/) | Data on 1.6M US nonprofits, grants, IRS compliance | partly (paid API) | yes | for recipient-side checks | yes | paid |
| LLM staleness research, e.g. [DyKnow](https://arxiv.org/abs/2404.08700v2) | Checks time-sensitive facts against Wikidata | yes | yes | method only; I found no ready tool that flags stale claims on web pages | n/a | n/a |

**David's version:** A yes. B yes. C real and modest: a directory whose claims you can trust is the whole value of the product. D yes, personal and unrelated to Unjournal money. E yes: it extends the existing weekly Action and writes static JSON. The one thing to avoid is checks that need him to review every flag each week.

**Progress.**
- *First milestone:* add a per-claim `source_url`, `last_checked` date and an archived snapshot. Make the weekly job fail loudly when importers return nothing. Have it fetch each source page, flag claims whose wording no longer appears, and show "last checked" honestly on the site. Test on the roughly 140 non-Pledge-1% claims: seed 10 known changes (a few real, a few planted in test copies) and measure how many the job flags against how many false alarms it raises.
- *One step past:* add a `reported_giving` claim type filled from certifying sources (1% for the Planet certification, public impact reports), and show pledge and reported giving side by side. Mark organizations with a pledge but no report in N years as "pledge only, unreported".

**Main risk:** false alarms from page redesigns and cookie banners. Matching on the claim sentence rather than the whole page, and having an LLM only judge pages that actually changed, keeps that down. The Pledge 1% bulk entries may simply need relabelling as "listed in showcase" rather than checked one by one.
