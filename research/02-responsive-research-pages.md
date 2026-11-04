# Idea 2: Responsive research pages

## Conclusion

Assemble it rather than build it, and treat it as a small project, not the ambitious one. Every part already exists. Hypothesis or GitHub Discussions collects public questions. A scheduled GitHub Action calls the model and posts a reply marked as an unreviewed draft. David endorses, edits or replaces the draft in the same thread. A build step copies endorsed answers into the static page. No server is needed. A first version is about two to four days of work, and model costs are a few dollars a month.

The real risk is demand, not engineering. David's existing "manual version" is not a reader Q&A loop. It is David reviewing his own drafts and Claude replying with what it changed. Across five of his sites, about 360 public Hypothesis annotations exist, and none come from outside readers. The only exception is a coauthor. If readers don't ask questions, the milestone metric ("share of answers I endorse without edits") has no data. The first milestone should therefore seed questions on purpose, and its pass condition should include a minimum number of real outside questions.

No existing tool does the specific loop: public question, AI draft marked unreviewed, then author endorsement. Docs widgets (kapa.ai, Mintlify) answer privately and give the owner analytics, not public endorsement. Paper platforms (alphaXiv, PubPeer) give authors a right of reply but either draft nothing with AI or only work for arXiv papers. That gap is real but narrow, and the gap alone doesn't show that people want the loop.

Against David's criteria it scores well on A, B and E. It scores weaker on C, because the benefit depends on traffic his pages may not get. It needs care on D, because two of the three most natural pilot pages are Unjournal pages and his annotations already mix the `daaronr` and `unjournal` accounts.

## What exists now: the manual version

The [author-reluctance note](https://unjournal-reluctance-note.netlify.app/) is a React single-page app that loads Hypothesis through `hypothes.is/embed.js`, with highlights always shown (checked in the page source).

The public Hypothesis API (`api.hypothes.is/api/search?uri=...`, queried 3 Nov 2026) shows what the loop looks like in practice:

| Page | Annotations | Who wrote them |
|---|---|---|
| [Author-reluctance note](https://unjournal-reluctance-note.netlify.app/) | 122, all June–July 2026 | `daaronr` 64, `unjournal` 58 |
| [Cultured chicken cost model](https://unjournal.github.io/cm_pq_modeling/) | 200 returned (216 total) | `daaronr` 135, `unjournal` 65 |
| [Just Ask the Model](https://llm-uj-research-eval.netlify.app/) | 12 | `daaronr` 6, `unjournal` 4, `valik` 2 (coauthor) |
| [Projects hub](https://projects.davidreinstein.org/) | 8 | `daaronr` 8 |
| [Animal Futures](https://uj-animal-futures-update.netlify.app/) | 3 | `unjournal` 3 |

On the reluctance note, David writes edit requests ("this needs a tooltip", "define Y"), and replies posted under the `unjournal` account begin "Claude:" and describe the revision made. That is a working author-to-AI revision loop on a public layer. It has not yet been a reader-to-author Q&A loop. It does show that David is comfortable reviewing AI output in Hypothesis threads, and that he already has an agent posting replies there, either directly through the API or by pasting. I could not tell which.

His GitHub ([github.com/daaronr](https://github.com/daaronr)) shows mostly static Quarto, bookdown and Netlify sites. The recently active personal projects are `impact-directory`, `opportunitycard`, `ea_giving_barriers`, `giveifyouwin`, `word2vecgames` and `music`. Several of these are good knowledge bases: long-form text in a repository that a model can read whole.

## Existing tools, checked

| Tool | What it actually does | Public-question + author-endorsement loop? | Open source / cost |
|---|---|---|---|
| **Hypothesis** | Public or group annotations on any web page. The API can create, update and search annotations, and replies are annotations that reference a parent ([API index](https://hypothes.is/api/)). On the public layer, flagged annotations are reviewed by Hypothesis staff; the page owner can't hide them ([moderation](https://web.hypothes.is/help/moderation-for-groups/), [IU KB](https://kb.iu.edu/d/atok)). Open groups, which any logged-in user can post to and whose creator moderates them, have historically been created by Hypothesis on request for partners ([groups post](https://web.hypothes.is/blog/expanding-our-groups-capabilities/)). Not verified whether users can now create them themselves. | Partly. It has public questions and threaded replies but no notion of endorsement. A tag or a reply convention can supply one. | Open source, free. |
| **giscus + GitHub Discussions** | Comment widget backed by GitHub Discussions; no backend; commenters need a GitHub account; moderation happens on GitHub ([giscus.app](https://giscus.app/)). Discussions support "mark as answer" by anyone with triage rights, plus lock, edit and delete ([GitHub docs](https://docs.github.com/en/discussions/managing-discussions-for-your-community/moderating-discussions)). Actions can trigger on `discussion` and `discussion_comment` `created` events (in public preview) ([GitHub docs](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows)). | Closest built-in fit. "Mark as answer" works as an endorsement, and the owner can edit or delete the bot's comment. | Free, open source. |
| **alphaXiv** | Line-by-line public comments on arXiv papers, AI chat on highlighted passages (changelog, Feb 2025), audio and an assistant ([changelog via search](https://www.alphaxiv.org/changelog), [Brown Institute](https://brown.columbia.edu/alphaxiv-seed)). Authors can link ORCID and reply; moderation combines LLM auto-moderation with community voting ([ZBW](https://openeconomics.zbw.eu/en/knowledgebase/alphaxiv/), [AIM](https://analyticsindiamag.com/ai-features/arxiv-is-great-but-what-if-you-deserve-better/)). The changelog page returned 404 when fetched directly, so these feature dates rest on search snippets. | No. The AI chat is private to the reader, and author replies are hand-written. arXiv papers only. | Closed, free to use. |
| **PubPeer** | Public comments on published papers. Authors are alerted automatically and have a "permanent right of reply"; anonymous comments are moderated before they appear ([FAQ](https://pubpeer.com/static/faq)). | No AI drafting. Covers papers with identifiers, not project pages. | Closed, free, donation-funded. |
| **NotebookLM** | Chat over uploaded sources. Audio Overviews come in formats such as Deep Dive, Brief, Critique and Debate, with a focus prompt and a length setting. Audio is downloadable and can be shared through public notebooks on consumer accounts. The help page warns overviews "may contain inaccuracies" and mentions no API ([Google help](https://support.google.com/notebooklm/answer/16212820)). | No. Readers' chats are private and the author never sees them. The audio has no script for the author to check before generating. | Closed, free tier. |
| **kapa.ai** | "Ask AI" widget for docs via a script tag; analytics on what people ask and where coverage is missing ([kapa.ai](https://www.kapa.ai/)). No public price list; Vendr reports a median of about $20.7k a year across 11 purchases ([Vendr](https://www.vendr.com/marketplace/kapa-ai)). The homepage describes no public answer-correction workflow. | No. Answers are private, with owner analytics. | Closed, expensive. |
| **Mintlify assistant** | Docs Q&A with cited sources, on the Pro plan and above, drawing on a monthly credit allowance. Usage analytics exist; the docs page doesn't say whether owners can review answers ([docs](https://www.mintlify.com/docs/ai/assistant)). | No. | Closed, paid; requires hosting on Mintlify. |
| **Dosu** | AI bot that gives a first-pass reply on GitHub issues and discussions; has "Response Previews" ([How to Dosu](https://dosu.notion.site/How-to-Dosu-48586039fe534a5baa818a9a87635ca1), [MIT AI Agent Index](https://aiagentindex.mit.edu/dosu)). Not verified that it supports approval before posting, or that it is free for public repositories (only a third-party listing says so). | Partly, on GitHub. Built for code repositories, not research pages. | Closed. |
| **Discourse AI bot** | Configurable AI personas inside a Discourse forum ([meta.discourse.org](https://meta.discourse.org/t/discourse-ai-ai-bot/266012.md)). No staff review queue for bot replies was found. | No. | Open source, but needs a server. |
| **X Community Notes** | Open-source "bridging" scoring algorithm; an AI Note Writer API since July 2025, where AI-written notes are rated by humans ([GitHub](https://github.com/twitter/communitynotes)). | It is the right model for "AI drafts, humans rate", but it only works on X. Useful as a design reference. | Algorithm open source. |

## Scores against David's criteria

Scale: ✔ meets, ~ partial, ✘ fails.

| Option | A. Public only | B. Testable v1 | C. Real payoff | D. Separation | E. Static, low attention |
|---|---|---|---|---|---|
| **David's proposal, assembled on Hypothesis + Action** | ✔ Reads only his public pages and repositories. | ✔ Endorse-without-edit rate is directly measurable from thread state. | ~ Valuable if readers ask questions; current evidence says they rarely do. | ~ Needs a personal bot account and a personal API key. Today's replies post under `unjournal`. | ~ Static page plus a cron Action. He can't hide spam on the public layer, so moderation depends on low traffic. |
| **David's proposal, assembled on giscus + GitHub Discussions + Action** | ✔ | ✔ "Mark as answer" is the endorsement signal. | ~ Same demand question; requiring a GitHub account cuts out many economists. | ✔ One repository per project; personal and Unjournal repositories are already separate organisations. | ✔ Static; he moderates fully; the Action runs only when a question arrives. |
| alphaXiv | ✔ | ✘ His projects aren't on arXiv. | ~ For arXiv papers only. | ✔ | ✔ Hosted, but not his to configure. |
| PubPeer | ✔ | ✘ No AI drafting; not for project pages. | ~ | ✔ | ✔ |
| NotebookLM (audio only) | ✔ | ✔ For audio: generate, listen, publish. | ~ Gets people to listen; the overview can't be checked before generation. | ✔ Use a personal Google account. | ✔ Manual, a few minutes per project. |
| kapa.ai / Mintlify | ✔ | ~ No endorsement loop to measure. | ~ | ✔ | ✘ Paid plan; Mintlify also needs its own hosting. |
| Dosu / Discourse AI | ✔ | ~ | ~ | ✔ | ✘ Discourse needs a server; Dosu's terms are unverified. |

## What progress looks like

**Design choice up front: where questions live.** Use giscus and GitHub Discussions as the default. It is the only option where David fully moderates, where "endorse" is a native action, and where the model call runs only in GitHub Actions with the key stored as a repository secret. Keep Hypothesis for passage-level questions on pages that already use it. The cost of giscus is that readers need a GitHub account. If that rules out his audience, Hypothesis is the fallback, accepting that he can't hide public-layer spam himself.

**Steps to the first milestone**

1. **Choose three personal projects, not Unjournal ones.** The reluctance note and the cultured-chicken model have the most annotation history, but they are Unjournal pages, and using them blurs criterion D. Better candidates: `ea_giving_barriers` (a long-form book), `opportunitycard` (papers plus discussion) and `impact-directory`. One Unjournal page can run in parallel under the `unjournal` organisation, with its own key and its own account.
2. **Build the knowledge base for each project as one file in its repository**, for example `kb/` containing the page source, linked papers and a short "positions I hold / things I don't claim" note written by David. The model reads it whole, so no retrieval system is needed.
3. **Write one reusable GitHub Action.** It triggers on a new discussion in a "Questions" category. It calls the latest Opus model (`claude-opus-5-5`) with the knowledge base cached. It posts a reply that begins with a fixed "Unreviewed AI draft — not yet checked by the author" banner and cites passages from the knowledge base. It adds an `unreviewed` label. Cost: Opus 5.5 is $4 input / $20 output per million tokens, with cache reads at $0.20. Fifty questions a month against a 50k-token knowledge base comes to roughly $2–12 a month, depending on cache hits.
4. **Define endorsement as states David sets on GitHub:** *endorsed* (mark the bot reply as the answer, unedited), *edited* (edit the reply, then mark it), *replaced* (write his own answer and mark that), *declined* (lock or close). An `edited_at` timestamp separates endorsed from edited.
5. **Add a build step** that pulls answered discussions and renders an "Asked and answered" section on each static page. Endorsed answers show his name; unreviewed drafts appear collapsed and clearly labelled, or not at all. Endorsed answers then appear on the page itself, not only in the widget.
6. **Seed questions on purpose.** Have the model generate about 15 likely reader questions per project, have two or three colleagues ask real ones, and post the project in the places where its readers already are. The demand evidence counts only the outside questions.
7. **Measure after about six weeks:** the endorse-without-edit rate, the shares edited, replaced and declined, the number of outside questions, and the minutes David spends per question. A useful pass condition is at least 20 outside questions across the three projects, with most endorsed or lightly edited, at under two minutes of his time each.

**One step past the milestone**

Add the checked audio explainer, with the script checked rather than the audio. The model writes a short script from the knowledge base plus the endorsed Q&A, David approves it like any other answer, and a text-to-speech service renders it in the same Action. NotebookLM's overview can't be checked this way, because it offers no script to approve before generation and no API. Endorsed Q&A from one project can also become a reusable FAQ, plus a style guide for the next project's drafts. Over time that should raise the unedited share.

**Hardest risk**

No one asks. The evidence from his own pages points that way, and the milestone metric silently depends on it. Second, an unreviewed AI answer sitting publicly next to his name could misstate his views before he sees it. Mitigations: the banner, holding drafts collapsed until he reviews them, and email notifications from GitHub. Third, on Hypothesis's public layer he can't remove abuse himself.

**Build vs. assemble**

Assemble. The only new code is a single Action of about 150 lines plus a render step, both reusable across every project. Building a custom Q&A widget or backend would break criterion E for no gain at his traffic levels.

## Friction noted

The alphaXiv changelog and the X Community Notes guide both refused direct fetches (404 and 402), so claims about them rest on search results and secondary sources. The Hypothesis API reference renders in JavaScript, so I used the live API index at `hypothes.is/api/` instead.
