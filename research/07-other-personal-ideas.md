# Other candidates: brass coach, micro course, workshop kit and Who's Available

Researched 3 November 2026. Scores use David's criteria: A everything public, B first version testable, C real payoff, D Unjournal and personal kept visibly separate, E cheap static hosting with no weekly attention. "Unverified" marks claims taken from app-store copy or search snippets that I could not check against the product itself.

## Ranking

1. **Brass coach that listens.** The best of the three. It is personal, public, testable and static, and David plays tuba, trombone and flugelhorn ([GTD Trio](https://daaronr.github.io/gtd-trio/)). Build it as the next step after reverse karaoke, reusing its timing map.
2. **Applied microeconomics self-study course.** The tooling is mature and free. Whether to build depends on one thing only: will David do the lessons? Test that with a two-week pilot before any real build.
3. **Workshop kit and Who's Available.** Skip both as the ambitious build. Both are Unjournal-side, both depend on a group adopting them, and Who's Available needs a server and holds people's contact details.

## 1. Brass coach that listens

### Conclusion

Worth building, and it is the most natural sibling to reverse karaoke. Brass apps that listen already exist, but none found does all three of the things David wants. They do not work in a browser for free, they do not handle tuba well (verified for none), and they do not write the next drill from what you just played. Commercial apps grade you against a fixed exercise library. The gap is the closed loop: play, get a timing and intonation report, get a new drill aimed at the weak spot.

The main risk is accuracy on low brass. Tuba fundamentals sit around 30–90 Hz, where browser pitch detectors need long windows and the phone or laptop microphone rolls off. Timing errors from audio latency are the second risk. Both can be measured in a day before anything else is built.

### What David already has

- **`transcribe.py`** in [daaronr/music](https://github.com/daaronr/music/blob/main/transcribe.py). A Python script that turns a recording into MusicXML. It uses an STFT-based monophonic pitch track and has instrument profiles for tuba (MIDI 34–65), flugelhorn (53–82) and bass. It runs offline, not in a browser, and assumes one constant tempo (see [04-reverse-karaoke.md](04-reverse-karaoke.md)).
- **[Jazz Practice Hub](https://jazz-practice-hub.netlify.app/).** It has a 12-key technique grid, a practice-plan generator that samples from his repertoire, and six metronome placements (beats to offbeats, 2 and 4, beat 4 only and so on). It saves ticks locally. It has no microphone input and does not adapt to how he played.
- **[Blues Flow](https://blues-flow.netlify.app/).** A Vite/TypeScript app with its own Web Audio engine (`blues-app/src/audio/engine.ts`). A browser coach could reuse its playback and backing tracks.
- **A private folder, `claude_code_misc_work/brass_playing_next_step/`.** The music repo's scripts reference it for a Kokoro text-to-speech setup. It is not public, so an outside builder cannot see what else is in it. Ask David whether any of it should be published.

### Comparables

| Tool | Brass handling | Adaptive drills | A | B | C | D | E |
|---|---|---|---|---|---|---|---|
| [tonestro](https://www.tonestro.com/) | 13 instruments including trombone and tuba per its site. Green/red feedback on notes and rhythm. Flugelhorn not listed. | No. Fixed teacher-made courses | n/a | yes | yes | n/a | no (subscription app) |
| [MakeMusic Cloud](https://www.makemusic.com/) (formerly SmartMusic) | Grades pitch and rhythm against the part, with four tolerance levels. Pitch grading reportedly ignores octave (from a search snippet of MakeMusic's help centre, which blocked direct fetching; unverified) | No. You choose repertoire; teachers assign | n/a | yes | yes | n/a | no (school subscription) |
| [TonalEnergy Tuner](https://tonalenergy.com/) | Strong tuner with intonation history and pitch-over-time plot. A reviewer notes brass can drown its reference tone without headphones | No | n/a | yes | yes | n/a | no (paid app) |
| [Yousician](https://yousician.com/) | No brass. Guitar, piano, bass, ukulele and voice only ([Wikipedia](https://en.wikipedia.org/wiki/Yousician)) | Yes, for those instruments | — | — | — | — | — |
| [Brass Practice](https://apps.apple.com/us/app/brass-practice/id6775900574) (iOS, 2026) | Imports MusicXML, scores pitch live and summarizes pitch, timing and sustain after each run. Trumpet, trombone and horn named | No. Has an "optional local AI coach", details not given (unverified) | n/a | yes | yes | n/a | free with ads, iOS only |
| [Neotones](https://mwm.ai/apps/neotones/6741388434) | Trumpet through tuba. Arban, Clarke and Concone exercises with play-along | Partly. An AI coach picks a daily routine from the fixed library based on history. The listing does not say it listens and grades (unverified) | n/a | yes | maybe | n/a | subscription |
| [Brassy](https://play.google.com/store/apps/details?id=app.brassy.brassy) | Long tones, note sprints, random notes with pitch analysis (store listing, unverified) | No | n/a | yes | maybe | n/a | Android app |

Building blocks, all public and free:

- **[pitchy](https://github.com/ianprime0509/pitchy).** McLeod Pitch Method in JavaScript. Returns Hz and a 0–1 clarity score, MIT licence, last pushed 1 Nov 2026. The obvious first choice for a browser tuner. Its accuracy on tuba is untested.
- **[CREPE](https://github.com/marl/crepe).** Neural pitch tracker with 360 bins of 20 cents (about six octaves), trained on 16 kHz audio. Python/TensorFlow and last pushed Aug 2024. The paper's lower bound is about 32.7 Hz (from memory, unverified), so tuba pedal tones would fall outside it.
- **[Basic Pitch](https://github.com/spotify/basic-pitch) / [basic-pitch-ts](https://github.com/spotify/basic-pitch-ts).** Spotify's note transcriber, instrument-agnostic, outputs MIDI with pitch bends, runs in the browser via TypeScript ([demo](https://basicpitch.spotify.com/)). Good for turning a whole take into notes after recording. The TS repo was last pushed May 2023.
- **[Essentia.js](https://github.com/MTG/essentia.js).** Onset detection and pitch algorithms (including YIN) compiled to WebAssembly.

### Scoring David's version

- **A: yes.** Everything is his own playing plus open libraries.
- **B: yes.** One exercise, one recording, one report can be checked against a tuner and a click by ear.
- **C: real but personal.** It helps one serious amateur practise better. It could help other low-brass players if it handles tuba, which commercial apps do poorly.
- **D: clean.** Purely personal, no money.
- **E: yes.** Everything runs in the browser: microphone capture, pitch detection, scoring and local storage. Drill generation can be rule-based with no model calls. An optional model call for written advice would need a key, so make it bring-your-own-key or leave it out.

### Progress

**First testable milestone: an honest report on one long-tone and one articulation exercise, on tuba and flugelhorn.** David plays a fixed exercise against a click: long tones on a scale, then quarter notes at 80 bpm. The page shows cents off per note, how steady each note held, and onset error in milliseconds per note. Pass condition: on ten takes, the per-note cents readings agree with TonalEnergy within about 5 cents, and onset errors agree with a hand-marked waveform within about 20 ms. Run a latency calibration first (play along to clicks through the speakers, measure the round trip). Bluetooth headphones will break timing.

**One step past: the next drill.** A rule set reads the last few reports and picks the next exercise. For example: if he is consistently flat on fifth-partial notes, set slow lip slurs into those notes; if he rushes the offbeats, reuse the Jazz Practice Hub's "2 and 4" placement at a lower tempo. Drills are generated as MusicXML or simple note lists, so they can be shown and played back. Success means David uses it for two weeks and the tracked weak spots move.

**Main risk:** pitch accuracy below about 60 Hz on laptop and phone microphones. If pitchy fails there, fall back to offline analysis with CREPE or Basic Pitch on the recorded take, which makes the loop slower but still static.

## 2. Applied microeconomics self-study course

### Conclusion

Building it is easy; the risk is that David won't do the lessons. The tooling to run R exercises with feedback on a static site is mature and free: [webR](https://github.com/r-wasm/webr) plus [quarto-live](https://r-wasm.github.io/quarto-live/), with [gradethis](https://github.com/rstudio/gradethis) for checking answers. Good open content exists too (Mixtape, The Effect, Econometrics with R, CORE). So the build adds little that is new. The only payoff is David actually learning, and he says so himself. Test that with a cheap two-week pilot before building more than a few lessons.

### What David already has

- **[Microeconomics (MSc) notes](https://daaronr.github.io/micro-giving-pub/)** ([repo](https://github.com/daaronr/micro-giving-pub), last pushed 1 Oct 2026). The planning page frames it as "Economics+ for EA+" and lists neglected topics: supply-demand and partial-equilibrium models for animal welfare, social welfare functions, eliciting risk and time preferences, crowding out in charitable giving.
- **A multiple-choice question bank**, `MCQs-Grid view.csv` in that repo. It has answers, hints, difficulty and share-correct figures from past Exeter exams (BEEM101, BEE2024), 2016–2024. That is intermediate micro, not applied micro, but it is a ready source of graded questions.
- **[Econometrics notes](https://daaronr.github.io/metrics_discussion/)** ([repo](https://github.com/daaronr/metrics_discussion)), and forks of [the Mixtape](https://github.com/daaronr/mixtape) and [Mostly Harmless replication](https://github.com/daaronr/mostly-harmless-replication) code.
- **A course format he has used before:** [AI Foundations for Research Judgment](https://ai-foundations-research-judgment.netlify.app/) and the [Prioritization ML Lab](https://uj-prioritization-ml-lab.netlify.app/) of AI-generated teaching simulations.
- None of his repos use webR, learnr or quarto-live yet (searched `micro-giving-pub` and `metrics_discussion`; the only hits are an old bundled `tutorial.js` asset).

### Comparables

| Tool | What it is | Runnable R with feedback | A | B | C | D | E |
|---|---|---|---|---|---|---|---|
| [quarto-live](https://github.com/r-wasm/quarto-live) + [webR](https://webr.r-wasm.org/) | Quarto extension. R and Python cells run in the browser, exercises with hints, solutions and custom grading, static hosting. 270 stars, last pushed Jun 2026 | yes | yes | yes | tool only | n/a | yes |
| [learnr](https://github.com/rstudio/learnr) + [gradethis](https://github.com/rstudio/gradethis) | Posit's tutorial package and answer checker. learnr needs a Shiny server; gradethis also works inside quarto-live | yes | yes | yes | tool only | n/a | no for learnr (needs a server) |
| [R Primers](https://r-primers.andrewheiss.com/) ([repo](https://github.com/andrewheiss/r-primers)) | Andrew Heiss's port of the old Posit Primers to Quarto and webR. Proof that the static route works for a full course | yes | yes | yes | data skills, not micro | n/a | yes |
| [swirl](https://github.com/swirldev/swirl) | Interactive lessons inside the R console | yes, local | yes | yes | old content | n/a | yes (no hosting) |
| [QuantEcon](https://quantecon.org/lectures/) | High-quality economics lectures. Python and Julia, not R | no R | yes | — | yes | n/a | yes |
| [Causal Inference: The Mixtape](https://mixtape.scunning.com/) / [Mixtape Sessions](https://www.mixtapesessions.io/) | Free book with R, Stata and Python code. The Sessions are paid live workshops | code, no grading | yes | — | yes | n/a | yes for the book |
| [The Effect](https://theeffectbook.net/) | Huntington-Klein's free causal-inference book with R code | code, no grading | yes | — | yes | n/a | yes |
| [Econometrics with R](https://www.econometrics-with-r.org/) | Free R companion to Stock and Watson. Exercise format not checked | unverified | yes | — | yes | n/a | yes |
| [CORE Econ](https://www.core-econ.org/) | Free economics textbooks with data exercises | partial | yes | — | yes | n/a | yes |
| [Khanmigo](https://www.khanmigo.ai/) | Khan Academy's AI tutor. A model of Socratic hints, but not about R or applied micro | no | n/a | — | — | n/a | no |

### Scoring David's version

- **A: yes.** Published papers with public replication data, plus open texts.
- **B: yes.** A lesson either runs and grades in the browser or it doesn't, and David either finishes it or doesn't.
- **C: uncertain.** It pays off only if David completes lessons, and the free material above already covers most of the standard ground. The distinctive angle is his own topic list (partial equilibrium for animal welfare, crowding out, welfare functions), worked through with real papers.
- **D: clean** as long as it stays a personal learning project. If the papers chosen are Unjournal-evaluated ones, link the public evaluations but keep the course on his personal site.
- **E: yes.** Static Quarto site with quarto-live. Model-written feedback on free-text answers would need an API key; leave it out of version one or make it bring-your-own-key.

### Progress

**First testable milestone: three lessons David actually completes in two weeks.** Pick one topic from his own list, such as cross-price elasticity of plant-based substitutes (which also feeds his Pivotal Questions workshop). Each lesson takes about 30 minutes and has a short simulation, one real paper with public data, and three graded R exercises in quarto-live. Pass condition: David finishes all three unprompted and says at least one changed how he reads a paper. If he doesn't finish them, stop. That answers his own question cheaply.

**One step past: a generator.** A script turns a paper with public replication data into a lesson draft: the setup, a simplified replication exercise, and gradethis checks against the published coefficients. David reviews and edits. This is where an AI expert adds something beyond existing courses, and it could later serve his students.

**Main risk:** David doesn't do the lessons. Second risk: webR package support. Packages that need compiled code not built for webR (some econometrics packages) won't load. Check `fixest` and `modelsummary` in the webR REPL before choosing papers (not checked here).

## 3. Workshop kit and Who's Available

### Conclusion

Not suitable as the one ambitious build. Both are Unjournal-side tools, both need a group to adopt them before their payoff can be tested, and Who's Available runs on a server and stores people's contact details. Each fails at least two of David's criteria. Any small improvements belong in-house.

### What they appear to be

The shortlist gives no detail, so these are inferences from his public sites.

- **Workshop kit.** The [Pivotal Questions workshops site](https://uj-pq-workshops.netlify.app/) repeats one pattern per workshop: a landing page, a summary or synthesis, a "Pivotal Questions" beliefs form, and a resources page. Supporting pieces include Metaculus forecasts, GitHub Discussions, a Coda question database and a scheduling form. The [Wellbeing workshop](https://uj-wellbeing-workshop.netlify.app/) adds explainers and calculators. A "kit" is most likely a template that turns this pattern into a repeatable package: scheduling, pre-reading, beliefs elicitation before and after, live notes, and a synthesis. A related prototype is the [Meeting Scheduler](https://unjournal-meeting-scheduler.netlify.app/meeting_scheduler/), branded "The Unjournal". It stores participants' names, emails, roles and time zones on a shared backend, and its role list includes evaluators.
- **Who's Available** ([live](https://info.unjournal.org/available/), [repo](https://github.com/daaronr/test_gitbook_schmooze_thing), last pushed 21 Jun 2026). People in a named "room" post short-lived cards: display name, availability window, topic, and "reach links" (phone, SMS, email, video). It also supports recorded voice prompts and replies. It is a Node, Express and Socket.IO server deployed on Render with a 1 GB disk. Availability lives in memory, while topics and voice clips persist in SQLite. The page says rooms have no access control, so anyone who knows a room name can see the cards. It sits on `info.unjournal.org`, though it is also listed on his personal hub.

### Comparables

| Tool | Covers | A | B | C | D | E |
|---|---|---|---|---|---|---|
| [Sessionize](https://sessionize.com/) | Calls for speakers and agendas | n/a | yes | for conferences | n/a | hosted SaaS |
| [pretalx](https://github.com/pretalx/pretalx) | Open-source call for papers and schedule | n/a | yes | for conferences | n/a | needs a server |
| [Indico](https://getindico.io/) | CERN's open-source event and workshop management | n/a | yes | yes | n/a | needs a server |
| [SHELF](https://shelf.sites.sheffield.ac.uk/) ([R package](https://cran.r-project.org/package=SHELF)) | Structured expert elicitation protocol and tools. The closest match to the beliefs form | yes | yes | yes | n/a | local R or Shiny |
| [Polis](https://github.com/compdemocracy/polis) ([pol.is](https://pol.is/home)) | Open-source group opinion mapping | n/a | yes | yes | n/a | hosted or self-hosted server |
| [Crab Fit](https://github.com/GRA0007/crab.fit) / [When2meet](https://www.when2meet.com/) / [Rallly](https://github.com/lukevella/rallly) | Group availability polls; Crab Fit and Rallly are open source | n/a | yes | yes | n/a | free hosted versions exist |
| [Cal.com](https://cal.com/) | Open-source booking links | n/a | yes | yes | n/a | free hosted tier |
| [Donut](https://www.donut.com/) | Slack app that pairs colleagues for chats | n/a | yes | yes | n/a | SaaS |
| [Kumu](https://kumu.io/) | Network and expertise mapping | n/a | yes | maybe | n/a | SaaS |

Scheduling is solved: Crab Fit or Rallly covers the Meeting Scheduler's job for free. What remains distinctive in the workshop pattern is beliefs elicitation before and after the workshop, tied to a synthesis. SHELF is the methodological comparable.

### Scoring David's versions

- **A: fails for both in practice.** The code is public, but the real test data are participants: workshop attendees' beliefs, and room members' names and contact links. The shortlist rules out internal records, and the scheduler's role list includes evaluators, whose identities are explicitly off limits.
- **B: weak.** A first version can be demoed, but whether it works only shows once a group adopts it, which an outsider cannot arrange.
- **C: modest.** Scheduling and availability already have good free tools.
- **D: fails.** Both are branded and hosted as Unjournal tools.
- **E: fails for Who's Available.** It needs a running server with a persistent disk. The workshop kit could be static, but beliefs forms need somewhere to store responses.

**Data flag.** Who's Available publishes people's phone numbers and emails in rooms with no access control. That conflicts with the public-only rule for any outside builder, who would need real rooms to test with. Separately, David's public repo [daaronr/schmoozer_app](https://github.com/daaronr/schmoozer_app), an early version of this idea, contains what looks like a third party's CV (a .doc résumé committed in Feb 2020). Worth telling David so he can decide whether to remove it.

### Progress (if David still wants them)

**First testable milestone: workshop kit as a Quarto template.** Extract the existing Pivotal Questions pages into a template repository. Use Crab Fit for scheduling and a SHELF-style before-and-after beliefs form. Pass condition: the planned plant-based substitution workshop gets its site from the template in under an hour. That is in-house Unjournal work, not a task for an outside builder.

**One step past:** a synthesis page that compares beliefs before and after the workshop and shows which ones moved. This overlaps with the forecast-to-decision workbench in [06-other-research-ideas.md](06-other-research-ideas.md).

**Main risk:** no one adopts them, and both handle personal data an outside builder shouldn't touch.
