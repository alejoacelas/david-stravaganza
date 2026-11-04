# #5 Evaluation distribution

Research date: 2026-11-03/04. Every claim has a link. Anything marked **unverified** I could not confirm.

## Conclusion

The stated milestone, "the full backlog appears on Sciety", cannot be reached by work on The Unjournal's side alone.

- Sciety only shows evaluations of papers hosted on seven preprint servers: bioRxiv, medRxiv, arXiv, OSF Preprints, PsyArXiv, Research Square and SciELO Preprints.
- About 5 of The Unjournal's 58 published evaluation packages are about papers on those servers. Most of the rest are NBER working papers (27), plus SSRN papers, journal articles and organisations' own websites.
- So reaching the full backlog needs the Sciety team (run by eLife) to change their code to accept NBER, SSRN and journal DOIs. They have no particular reason to prioritise economics.

The more urgent finding is The Unjournal's own DOI metadata. That metadata is what every downstream service reads, and it is incomplete and inconsistent:

- 43 of the 107 DOIs that The Unjournal lists on RePEc do not resolve. They were never registered with Crossref.
- Individual evaluations are registered as "component" records with no link to the paper they evaluate.
- Summaries from 2026 are registered as "journal-article" instead of "peer-review", and they lack the `is-review-of` link.
- Template and "DELETE ME" test records are live in Crossref.

Repairing this is cheap, entirely public, and fully in The Unjournal's control. It is the precondition for Sciety, OpenAlex and anything else.

**Recommendation:** reframe the project as "make every Unjournal evaluation correctly machine-linked to its paper", in three steps:

1. Audit and fix the metadata.
2. Push the 5 eligible papers to Sciety now.
3. Ask Sciety to accept NBER/SSRN DOIs, backed by evidence.

This is mostly metadata work plus emails, with a small script that can be checked into a repository. It is a modest fit for an outside AI expert. It is too small to be "one ambitious thing", but it is a strong first two weeks, or a module of a larger build.

## Current state (verified)

### Sciety

- **The Unjournal already has a Sciety group,** with 10 followers ([group page](https://sciety.org/groups/the-unjournal)). It shows one article, "Long Term Cost-Effectiveness of Resilient Foods…", with 4 evaluations, last active 5 January 2023 ([group page](https://sciety.org/groups/the-unjournal); [lists page](https://sciety.org/groups/the-unjournal/lists)).
- **Sciety finds Unjournal evaluations through the Hypothes.is account `theunjournal`,** and only that way ([Sciety ingestion config, `discoverEvaluationsFromHypothesisUser('theunjournal')`](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/evaluation-discovery-processes.ts)).
- **That account has 9 annotations in total** ([Hypothesis API](https://api.hypothes.is/api/search?user=acct:theunjournal@hypothes.is)):
  - 4 are on `osf.io/vrmpf`, dated January 2023. These are the four Sciety shows.
  - 5 are on an NBER PDF (w23928), dated February 2023. Sciety silently dropped these because NBER is not a supported server.
  - The account has not been used since.
- **The server restriction is hard-coded.** Sciety turns a paper URL into a DOI only for these DOI prefixes ([config](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/expression-doi-from-uri-config.ts); [parser](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/supported-expression-doi-from-uri.ts)):

  | Server | DOI prefix |
  |---|---|
  | bioRxiv / medRxiv | 10.1101, 10.64898 |
  | Research Square | 10.21203 |
  | SciELO Preprints | 10.1590 |
  | OSF Preprints | 10.31219 |
  | PsyArXiv | 10.31234 |
  | arXiv | 10.48550 |

  - Not supported: NBER (10.3386), SSRN (10.2139), MetaArXiv (10.31222) and all journal DOIs.
- **Sciety dates Hypothesis-based evaluations by when the annotation was created.** It also only scans the last few days of annotations (`INGEST_DAYS`, default 5) ([converter](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/evaluation-discovery/hypothesis/convert-hypothesis-annotation-to-evaluation.ts); [config](https://github.com/sciety/sciety/blob/main/src/ingest/generate-configuration-from-environment.ts)). So posting backlog annotations today would show them as "evaluated in November 2026", not on their real dates.
- **Sciety is still maintained.** Its last code commit was 22 October 2026 ([repo](https://github.com/sciety/sciety)). In January 2026 it moved all per-group ingestion code into a "legacy" folder ([commit history](https://github.com/sciety/sciety/commits/main/src/ingest/legacy/evaluation-discovery-processes.ts)). The newer route is a COAR Notify inbox, and it is currently wired only for PCI ([inbox reader](https://github.com/sciety/sciety/blob/main/src/ingest/coar/retrieve-coar-notifications-by-group.ts)). **Unverified:** whether Sciety plans to move new groups onto COAR Notify, or is still adding groups at all. I found no 2026 roadmap.

### Crossref

The Unjournal's DOIs are registered by PubPub (Knowledge Futures, Crossref member 9621, [prefix 10.21428](https://api.crossref.org/prefixes/10.21428)), not by The Unjournal itself. I pulled all 14,074 records under that prefix and kept the 106 Unjournal ones (`10.21428/d28e8e57…`), using the [Crossref REST API](https://api.crossref.org/prefixes/10.21428/works).

**What exists:**

| Record type | Count | What it is |
|---|---|---|
| `peer-review` | 42 | "Evaluation summary and metrics" records. All 42 carry `is-review-of` pointing at the paper's DOI. |
| `component` | 49 | Individual evaluations, as sub-DOIs (e.g. `…680752e4/6998ae60`). None has an `is-review-of` link. Crossref says components can't be attached to peer-review records ([Crossref peer review docs](https://www.crossref.org/documentation/research-nexus/peer-reviews/)). |
| `journal-article` | 13 | Mostly author responses, linked with `is-reply-to`. Also two 2026 evaluation summaries ("Does Conservation Work…", "Universal Basic Income…") that should be `peer-review` records with `is-review-of`. |
| `posted-content` | 1 | A test record titled "DELETE ME Evaluation summary and metrics…". |

- The 42 `peer-review` records include one template, "Title of paper (template)", that claims to review a real paper (`10.3200/jece.38.1.124`).
- **The papers those `is-review-of` links point at:** 39 distinct papers. 25 are NBER, 5 SSRN, 3 MetaArXiv, and 6 are journal articles (AER Insights, AEA P&P, AEJ: Policy, Nature, and others). None is on a server Sciety supports.
- **Links to DOIs that do not exist:** 7 internal relations point at Unjournal DOIs that return 404 at doi.org, for example `10.21428/d28e8e57.1809195c`.
- **DOIs advertised on RePEc that do not resolve:** The Unjournal's own RePEc export files list 107 DOIs ([pypubpub/repec_rdfs](https://github.com/unjournal/pypubpub/tree/main/repec_rdfs)). 43 of them return 404 at doi.org.
  - The problem is getting worse: 13 of 22 in the latest batch (`eval2025_04.rdf`) fail, against 2 of 11 in 2023.
  - Example: `10.21428/d28e8e57.7302639b`, the summary for "Asymmetry in Civic Information…".
  - Most likely cause (**unverified**): PubPub assigns a DOI when the page is drafted, but registration only happens when someone clicks "deposit", and that step was skipped.

**How big the backlog is.** The Unjournal's public data repository lists 58 papers with status "published evaluations" ([research.csv](https://github.com/unjournal/unjournaldata/blob/main/data/research.csv)). Their DOIs or URLs:

| Where the paper lives | Count |
|---|---|
| NBER (10.3386) | 27, plus 1 NBER URL |
| Various journals | ~13 |
| Organisations' own websites, Dropbox, Google Docs | ~9 |
| SSRN (10.2139) | 3 |
| arXiv (10.48550) | 3 |
| OSF (10.31219) | 1 |
| Research Square (10.21203) | 1 |

So about 5 of 58 are on servers Sciety supports. Crossref has `peer-review` records for roughly 40 of the 58.

### OpenAlex

- 58 of the 106 Unjournal DOIs are in OpenAlex. That covers all 42 `peer-review` records, typed `peer-review`. Most component records (the individual evaluations) are missing ([OpenAlex API query](https://api.openalex.org/works?filter=doi:10.21428/d28e8e57.10e0adbf)).
- "The Unjournal" is not an OpenAlex source. The summary records have no source attached ([example record](https://api.openalex.org/works/doi:10.21428/d28e8e57.10e0adbf)).
- OpenAlex has no "reviews of this work" field. For only 8 of the 42 summary records does the reviewed paper appear in their `referenced_works`. So OpenAlex mostly does not connect an evaluation to the paper it evaluates. I checked each of the 42 through the API.

### RePEc (the venue that matters most in economics)

- The Unjournal already publishes its evaluations to RePEc as its own series, `RePEc:bjn:evalua` ([IDEAS series](https://ideas.repec.org/s/bjn/evalua.html); [EconPapers](https://econpapers.repec.org/paper/bjnevalua/)). The upload uses scripts in [unjournal/pypubpub](https://github.com/unjournal/pypubpub).
- The records carry no pointer to the evaluated paper. They contain only title, abstract, DOI and URL ([eval2025_04.rdf](https://github.com/unjournal/pypubpub/blob/main/repec_rdfs/eval2025_04.rdf); [sample IDEAS page](https://ideas.repec.org/p/bjn/evalua/e1chooseyourmoments.html)). So the NBER paper's IDEAS page does not show that it was evaluated.
- **Unverified:** whether RePEc's record format has any "comment on" or "review of" field, or whether CitEc would count an evaluation as citing the paper if a reference list were included. Only RePEc's maintainers can answer this; see "who must cooperate" below.
- The Unjournal's data repository also has an `ssrn_crosspost_mapping.csv` mapping 33 papers to their SSRN pages ([file](https://github.com/unjournal/unjournaldata/blob/main/data/ssrn_crosspost_mapping.csv)). **Unverified:** whether evaluations are actually posted to SSRN today.

## How other review groups do it (verified)

**How Sciety ingests other groups** ([config](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/evaluation-discovery-processes.ts)):

| Route | Groups using it |
|---|---|
| Hypothes.is group or user | eLife, Review Commons, Biophysics Colab, ScreenIT, Arcadia, PeerRef, GigaScience, ASAPbio, The Unjournal |
| Custom feeds or APIs | PREreview (API), Rapid Reviews (custom), preLights (feed) |
| RSS | PCI communities |
| Crossref | PeerJ only. The code walks bioRxiv's list of published papers and then looks for Crossref review DOIs, so it is not a general "find `peer-review` records with `is-review-of`" ingest ([code](https://github.com/sciety/sciety/blob/main/src/ingest/legacy/evaluation-discovery/discover-evaluations-from-crossref-via-biorxiv.ts)). |
| COAR Notify inbox, then DocMap | PCI ([code](https://github.com/sciety/sciety/blob/main/src/ingest/coar/discover-pci-evaluations.ts)) |
| DocMaps from Kotahi | Behind an experiment flag only |

Sciety sends COAR Notify messages for PREreview (to a sandbox) and Biophysics Colab (to a Kotahi staging inbox) ([config](https://github.com/sciety/sciety/blob/main/src/read-models/evaluations-for-notifications/coar-notifications-config.ts)).

**COAR Notify.** A review service posts a small JSON-LD message announcing a review to a repository's inbox, using W3C Linked Data Notifications ([COAR slides, June 2026](https://coar-repositories.org/wp-content/uploads/2026/06/1.2.-Notify-and-Peer-Review-Paul-Walk.pdf)).

- **Who implements it:** the [official catalogue](https://coar-notify.net/catalogue/implementations/) lists 16 implementations, including HAL, DSpace, EPrints, Dataverse, Episciences, PCI, PREreview, Kotahi and Sciety.
  - bioRxiv and SciELO appear only for sending review requests to PREreview.
  - arXiv, OSF, Zenodo and medRxiv are not listed.
- **Which repositories show reviews on the paper page:**
  - HAL, for PCI recommendations ([PCI](https://peercommunityin.org/2024/01/15/submission-from-hal/)).
  - EPrints with the PCI plugin ([wiki](https://wiki.eprints.org/w/COAR_Notify:_PCI)).
  - DSpace 7/8 stores review links, but only from senders it has registered as trusted, and it may hold them for moderation ([COAR](https://coar-repositories.org/news-updates/coar-notify-functionality-now-available-to-dspace-users/)).
  - Cambridge Apollo moderates every message and asks senders to make contact first ([Apollo](https://www.repository.cam.ac.uk/info/coar-notify-support)).
- **OSF:** COAR lists the Center for Open Science's servers as "discussions only" ([COAR update](https://coar-repositories.org/news-updates/the-expanding-coar-notify-ecosystem-project-update/)).
- **Zenodo:** support (through InvenioRDM) is still in testing, according to the same June 2026 slides.
- **Sending is cheap:** the `coarnotify` Python library builds, validates and sends messages ([PyPI](https://pypi.org/project/coarnotify/)).

**Economics venues.** None of NBER, SSRN, RePEc, CEPR or IZA accepts COAR Notify or any other way for an outside reviewer to get a link shown on the paper's page. This is a plain "no route exists" for the venues that host most Unjournal papers.

- Checked: NBER, SSRN and RePEc. For CEPR and IZA I found nothing, but did not search them specifically (**unverified**).
- The World Bank's Open Knowledge Repository runs DSpace 7, so it could in principle receive COAR Notify messages ([Atmire](https://www.atmire.com/news-case-studies/upgrading-the-world-banks-open-knowledge-repository-to-dspace-7)). I found no sign that it does (**unverified**).
- EconStor's DSpace version and Notify status are unknown (**unverified**).

**Crossref Event Data,** the old route for finding "who links to this DOI", was shut down on 23 April 2026. Only a narrower data-citation endpoint replaces it ([Crossref blog](https://crossref.org/blog/strengthening-support-for-data-citations-and-saying-goodbye-to-event-data)). Building on Event Data is therefore not an option.

**Crossref peer-review rules:** every review must carry a relation to the reviewed item, and that item must itself have a Crossref DOI ([Crossref docs](https://www.crossref.org/documentation/research-nexus/peer-reviews/)). Most Unjournal targets qualify: NBER, SSRN and journals all have Crossref DOIs. Papers that live only on organisations' websites do not, and cannot be linked this way.

## Scores against David's criteria

Scale: ✔ good, ~ partial, ✘ poor.

| Route | A. Public only | B. First version testable | C. Real payoff | D. Separate from money | E. Cheap, low upkeep | Note |
|---|---|---|---|---|---|---|
| **David's version** (all four channels plus every repository, full backlog on Sciety) | ✔ | ✘ | ~ | ✔ | ~ | Milestone blocked by Sciety's server list. Repository links mostly have no receiving end in economics. |
| **Crossref metadata audit and fix** | ✔ | ✔ | ✔ | ✔ | ✔ | Fully within The Unjournal's control, once PubPub (or whoever in the team deposits DOIs) re-deposits. Fixes the base everyone else reads. |
| **Sciety via Hypothesis** (the existing route) | ✔ | ✔ | ~ | ✔ | ✔ | Works today, but only for about 5 of 58 papers, with wrong dates on backlog items. |
| **Sciety via code change** (accept NBER, SSRN and journal DOIs, read Crossref `is-review-of`) | ✔ | ~ | ✔ | ✔ | ✔ | Needs the Sciety team to agree, or to accept a pull request. Sciety already reads paper metadata from Crossref, so it is technically plausible (**unverified** effort). |
| **COAR Notify sender** | ✔ | ~ | ✘ | ✔ | ✔ | Cheap to send, but no economics venue is listening. Only worth it if a DSpace venue such as the World Bank OKR registers The Unjournal as a trusted sender. |
| **OpenAlex** | ✔ | ✔ | ~ | ✔ | ✔ | Nothing to build. It mirrors Crossref. Getting "The Unjournal" listed as a source would need a request to OpenAlex support (**unverified** process). |
| **RePEc link to paper** | ✔ | ~ | ✔ | ✔ | ✔ | The audience economists actually see. Depends on RePEc having a suitable field (**unverified**). |

## What progress looks like

### Steps to the Sciety milestone

1. **Audit (about 1–2 days, a script).** Pull every Unjournal DOI from Crossref, the RePEc export files and `research.csv`. Produce one table: each package; its summary and evaluation DOIs; whether each DOI resolves; its record type; whether it carries `is-review-of`; the paper's DOI; and whether that paper is on a server Sciety supports. Everything above came from public APIs in under an hour, so this is fast.
2. **Repair (Unjournal staff work in PubPub, and possibly a PubPub support ticket).**
   - Register the 43 DOIs that don't resolve.
   - Retype the 2026 summaries as `peer-review` and add `is-review-of`.
   - Remove the template and "DELETE ME" test records from Crossref.
   - **Unverified:** whether PubPub's interface lets The Unjournal give individual evaluations their own `is-review-of` link, or only the summary pub. Crossref forbids components on `peer-review` records, so individual evaluations may need to become separate top-level pubs.
3. **Quick Sciety win.** Post Hypothesis annotations from `theunjournal` on the roughly 5 papers that live on arXiv, OSF and Research Square. Each annotation links to the evaluation. They should appear on the existing group page within a day. Dates will show as today unless Sciety backfills them; ask.
4. **The real milestone needs Sciety.** Email the Sciety team with the audit table and ask for one of two changes:
   - (a) accept NBER, SSRN and journal DOI prefixes for The Unjournal, or
   - (b) a Crossref-based ingest that reads The Unjournal's `peer-review` records and their `is-review-of` links.
   Option (b) would also serve any other group that registers reviews properly. Offer a pull request; the codebase is public TypeScript.

### One step past it

Get the evaluation shown where economists look:

- Ask RePEc's maintainers whether a record format field or CitEc reference can make the NBER paper's IDEAS page show "evaluated by The Unjournal". Then add that field to the existing RePEc export in `pypubpub`.
- Add a small scheduled check, for example a GitHub Action, that fails when a newly published package has a DOI that doesn't resolve or lacks `is-review-of`. That stops the gap from coming back without David watching it.

### Who outside must cooperate

| Who | What they need to do |
|---|---|
| Sciety team (eLife) | Change which servers they accept. This is the gating dependency. |
| PubPub / Knowledge Futures | Only if the repair needs deposits or relation types the PubPub interface can't do. |
| RePEc maintainers | Answer whether a linking field exists. |
| OpenAlex | Optional: list The Unjournal as a source. |
| Crossref | Nothing; PubPub deposits on The Unjournal's behalf. |
| NBER, SSRN | No mechanism to ask for. |

### Biggest risk

Sciety says no, or says "later". Then the headline milestone stalls with about 5 papers shown, however good the build. A second risk: Sciety appears to be moving away from the per-group ingestion code The Unjournal relies on (it was moved to "legacy" in January 2026), and its long-term direction is unverified.

### Build, or mostly metadata and emails?

Mostly metadata and emails. The code is:

- an audit script (a few hundred lines),
- an optional Hypothesis poster for eligible papers,
- an optional pull request to Sciety,
- a CI check.

The value comes from a clean link between each evaluation and its paper, and from persuading two or three outside teams.

### Fit for an outside AI expert

Weak as "the one ambitious thing". The hard parts are not AI work: persuading Sciety and RePEc, and clicking through PubPub deposits, which only Unjournal staff with PubPub access can do. AI-assisted coding makes the audit fast, but it is a small job.

It is a good small companion task to another build, for example the research reviewer or impact tracker on the shortlist. Those also depend on a reliable link from each evaluation to its paper, and the audit table is reusable input for them.

## Not verified

- Whether the Sciety team would accept NBER, SSRN or journal DOIs, or a general Crossref ingest; and Sciety's 2026 plans.
- Whether PubPub's interface can set `is-review-of` on individual evaluations, and why 43 DOIs were never registered.
- Whether RePEc or CitEc has any mechanism to link a comment to the paper it comments on.
- Whether The Unjournal currently cross-posts evaluations to SSRN.
- The status of COAR Notify at CEPR, IZA, EconStor, the World Bank OKR, arXiv and Zenodo.
- Whether my count of 106 Unjournal Crossref records is complete. I pulled the whole 10.21428 prefix. Any Unjournal DOI registered under a different prefix would be missed.
- The 58-paper backlog figure comes from The Unjournal's own public `research.csv`. I could not cross-check it on unjournal.pubpub.org because the site served a Cloudflare challenge to scripted requests.
