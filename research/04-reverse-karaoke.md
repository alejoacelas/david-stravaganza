# Idea 4: Reverse karaoke with real musical timing

## Conclusion

Most of this already exists. Soundslice does nearly everything on David's list in a browser for $5 a month. It has editable bar and inner-bar timing, a click that follows the recording's tempo, a count-in at the local tempo before each loop, pickup bars and drag-to-loop. Capo does most of the same on Mac and iPhone, with editable beats and downbeats. So do not start by building a player.

Start with one evening of testing instead. Load David's "troublesome recordings" into a one-month Soundslice Plus trial and into Capo's free edition, and write down exactly where each one fails. Build only for the failures that remain.

Three gaps are likely to survive that test, and together they are a real but small project:

1. **Entrances out of rubato.** Existing tools count you in from a steady pulse. They do not give a cue such as "you come in after the piano's fermata, two beats into the vamp". That is the hard case for a horn player.
2. **Open, portable timing maps.** David already writes iReal Pro links and MusicXML for his charts. He would want a beat map he owns, stored as a plain file next to the chart, with no subscription to keep it alive.
3. **Feedback on his own entrance timing.** Did he come in early or late? This leads straight into his sibling idea, "Brass coach that listens".

If he does build, build a small static web app. It would analyse audio in the browser with an existing beat tracker that already runs there, and it would put a fast correction screen in front of a person. Nothing like that exists yet. The hard problem is not playback. It is getting a correct beat and bar map for an expressive jazz recording in a few minutes of human correction.

## What David has now

His earlier reverse-karaoke prototypes are not public. I checked the projects hub (https://projects.davidreinstein.org/#music) and all 63 public repos at https://github.com/daaronr. None of them is a play-along tool for real recordings. Ask him for those prototypes and his list of troublesome recordings. Both are the real starting point.

Here is what is public:

- **Blues Flow** (https://blues-flow.netlify.app, source in `blues-app/` of https://github.com/daaronr/music). It plays 18 twelve-bar blues forms with a synthetic trio "at any tempo, with a count-in", shows lead sheets in concert, B♭ and E♭, and has a chart parser (`src/music/parse.ts`). **Shortfall:** the backing is synthetic at a constant tempo, with no real recordings. Its README also describes "a nudge to donate to The Unjournal or GiveWell instead of paying, with a form to say you did". That mixes personal projects with Unjournal money, which criterion D warns against.
- **Jazz Practice Hub** (https://jazz-practice-hub.netlify.app, `jazz_hub/index.html`). It has a repertoire tracker and metronome drills, plus intro and ending presets such as "2-bar pickup", "Rubato head → time" and "Ritard to button on I". **Shortfall:** these are text presets. Nothing plays audio against them.
- **`transcribe.py`** (https://github.com/daaronr/music/blob/main/transcribe.py). It transcribes a melody from audio to MusicXML and has profiles for flugelhorn and tuba. Its `infer_tempo_and_repeats` assumes one constant tempo across the whole recording and no pickup. It divides the recording's duration by the bars in the form and picks the tempo closest to 100 BPM. That is exactly the assumption that breaks on his troublesome recordings.
- **A notation pipeline** in `claude_halation/`, `claude_parallax/` and `skills/ireal-pro-chart/`: text notation to MusicXML to MuseScore, plus generators for iReal Pro links. This is useful. Charts for the new tool can come from files he already makes.

## Existing tools, verified

| Tool | Follows tempo drift / rubato | Editable beat & bar map | Pickups & entrance cues | Loop by bar | Synced chart | Price, platform |
|---|---|---|---|---|---|---|
| **Soundslice** | Yes. Bar syncpoints plus inner-bar syncpoints. "Guide notes" let you sync note by note in rubato.[1][2] | Yes. Tap T per bar, then drag. Auto-sync from notation creates "inner-bar syncpoints for rubato passages"; "Detect beats" needs 3 manual syncpoints. Detected beats with snap since Aug 2026.[2][3] | Pickup bars are supported.[4] Count-in "uses whatever the tempo of the recording is, at the moment at which your playhead is set", with options for 1 to 3 bars and "before each loop".[5][6] There is no cue tied to a rubato entrance. | Yes. Drag over the music; saved "clips".[7] | Yes. Full notation or chords, synced to audio.[7] | Free tier can't attach MP3s or auto-sync; Plus is $5/mo or $50/yr. Browser. API only on Teacher ($20/mo) or Licensing.[7][8] |
| **Capo** (SuperMegaUltraGroovy) | Partly. It maps the eighth-note pulse "allowing it to handle a little bit of drift"; downbeat estimation "is unable to work with odd or changing time signatures".[9] | Yes. "Correct downbeat locations and adjust beats per bar … tempo changes".[10] | Count-in "gives you a bar or two"; metronome follows the stored beats.[9][10] No rubato cues. | Yes. Loops snap to bars.[10] | Detected chords, editable. No notation.[11] | Free edition doesn't save beat edits; Pro is $39.99/yr on Mac or $19.99/yr on iOS. Mac and iOS only, on-device.[12] |
| **Moises** | Says its smart metronome "will follow any BPM variation".[13] | Bars and beats shown with chords.[14] **I could not verify** that users can correct beats or downbeats in the practice app. Chord editing on a bar/beat grid exists in AI Studio (Pro).[15] | Count-in of up to 16 clicks on paid plans.[16] | Loop a selection; AI-detected sections.[16] | Detected chords. | Separates "wind instruments" on Premium.[17] Web, desktop, mobile. Price not verified (shown only after login). |
| **Anytune** | No. Count-in uses "the song's BPM", a single value.[18] | Marks only, no beat grid.[19] | Visual and audible count-in; Tap-In to start in time.[18] | Loops between marks.[19] | Lyrics/text only. | Free; Pro+ $14.99; Mac $35. iOS and Mac.[19][20] |
| **Transcribe!** | Manual. You tap measure markers, then "auto subdivisions" for beats.[21] | Yes, by hand (markers). | Section markers with labels. No count-in found. | Named loops.[22] | Chord *guesses*, not a chart.[22] | $39 one-time. Windows, Mac, Linux.[23] |
| **Amazing Slow Downer** | No. | No. Loop points only. | Delayed start only. | Time-based loops, not bar-based.[24] | No. | $39.95 desktop, $14.95 iOS, $9.95 Android.[25] |
| **iReal Pro** | Not applicable: synthetic band, not recordings. | — | Count-in, loop any section.[26][27] | Yes. | Yes (it is the chart). | $21.99 iOS, one-time per platform.[28] |
| **Chordify** | Automatic beat tracker. You can only "shift" chords against bar lines; the grid itself isn't editable.[29] | No. | No. | — | Chords on a beat grid.[30] | Upload needs Premium; $24–54/yr. Web and apps.[31] |
| **Sonic Visualiser** | Via plugins (QM Bar and Beat Tracker).[32] | Yes. Tapped, editable "time instants" with bar/beat numbering. Used by the Jazzomat project to annotate jazz solos.[33][34] | No. | Selection snaps to instants. | No. | Free and open source. Desktop. An analysis tool, not a practice tool. |
| **Aebersold (JazzBooks Streaming), Music Minus One** | Recorded *for* play-along, so the problem mostly doesn't arise. | No. | Count-ins are recorded on the tracks. | Tempo/key change; MMO's Playback+ has loop points.[35][36] | Separate books. | Subscriptions or books. Fixed catalogue, not your own recordings. |

Libraries David's version would use:

- **Beat This!** (CPJKU, MIT licence, ISMIR 2024). Tracks beats and downbeats without assuming a fixed meter or tempo. The authors say it "can still fail, especially for difficult and underrepresented genres, and performs worse on continuity metrics" (https://github.com/CPJKU/beat_this, https://arxiv.org/html/2407.21658). It **already runs in the browser.** `@jgorset/beat-this` uses ONNX Runtime Web with WebGPU or WASM and an 83 MB model (https://socket.dev/npm/package/@jgorset/beat-this). Another project measured a 3-minute song analysed in 13.9 s on an Intel Iris Xe laptop GPU (https://huggingface.co/6l3m/kairos-music).
- **madmom.** Its beat and downbeat tracker has been ported to Rust and WASM (https://github.com/creightonlinza/madmom-beats-port).
- **Essentia.js.** WASM, **AGPLv3**, includes RhythmExtractor2013 (https://transactions.ismir.net/articles/10.5334/tismir.111). The AGPL is fine for an open-source static site but is a constraint to know about.
- **wavesurfer.js.** Its Regions plugin gives draggable markers and regions that can loop (https://wavesurfer.xyz/docs/plugins/regions/). It is a good base for the beat-map editor.
- **Demucs in the browser.** Several ports exist (https://github.com/bakkot/demucs-js, https://stemsplit.github.io/demucs-onnx/browser/). The standard 4-stem model outputs drums, bass, vocals and "other" (https://github.com/timcsy/demucs-web), so **a trumpet or sax lands in "other" with the piano.** Removing the soloist from a band recording is not solved by open models. Moises claims a wind stem. I did not test its quality.
- I did not check BeatNet or Spleeter in depth. Beat This! is newer and already has a browser port, so neither is needed.

## Scores against David's criteria

Scale: ✓ good, ~ partial, ✗ poor. For existing tools, B and C mean "how far it gets David to his milestone today".

| | A. Public inputs | B. Testable first version | C. Real payoff | D. Unjournal kept separate | E. Cheap, static, low upkeep |
|---|---|---|---|---|---|
| **Soundslice** | ✓ his own files | ✓ testable this week | ✓ covers most of the milestone; weak on rubato entrances | ✓ | ~ $50/yr; data sits in their service, though syncpoints can be exported as a file[37] |
| **Capo** | ✓ | ✓ | ~ strong beat editing, no notation, Apple only | ✓ | ~ $40/yr Mac |
| **Moises** | ✓ (uploads audio to their servers) | ✓ | ~ good click and stems; beat correction unverified | ✓ | ~ subscription |
| **Transcribe!** | ✓ | ✓ | ~ manual markers, no synced click | ✓ | ✓ $39 once |
| **Anytune / Amazing Slow Downer** | ✓ | ✓ | ✗ fixed-tempo count-in or none | ✓ | ✓ one-time |
| **iReal Pro / Aebersold / MMO** | ✓ | ✓ | ✗ not his recordings | ✓ | ✓ |
| **Chordify** | ✓ | ✓ | ✗ grid not editable | ✓ | ~ |
| **Sonic Visualiser** | ✓ | ~ maps yes, practice no | ~ good for making maps only | ✓ | ✓ free |
| **David's proposed tool** | ✓ The app and maps can be public. **The app must not ship or host audio.** Users load local files and nothing is uploaded. A beat map holds only timings, so sharing maps is very likely fine; I have not checked this legally. Demos should use his own band recordings, with bandmates' consent, or public-domain recordings. | ✓ "Play along with my troublesome recordings" can be checked tune by tune (see below). | ~ Real for David, and for horn players who practise against old records. The extra value over Soundslice is the three gaps above, not the whole feature list. | ✓ Easy, as long as it does not copy Blues Flow's Unjournal donation nudge. Use the hub's personal support route instead (shortlist idea 3). | ✓ Static hosting, analysis in the browser, nothing stored on a server. The costs are an 83 MB model download on first use and WebGPU for speed. No weekly upkeep. |

## What progress looks like

**Step 0: decide build or not (one evening).** Pick 5 troublesome recordings. For each, note the failure: rubato intro, pickup, tempo drift, a ballad tracked at double time, a meter change, or no chart. Try each in a Soundslice Plus trial (auto-sync, then fix) and Capo free. Time how long it takes to get a playable map. If both handle all five in under 10 minutes each, stop. Write a short workflow note and use Soundslice. The only build would then be a converter from his iReal/MusicXML charts into Soundslice, and he already has most of it.

**Path to the milestone if gaps remain:**

1. **Timing-map format.** A JSON file with beats (time, bar, beat in bar), meter changes, a pickup offset, section labels and **cue events** (a timestamp with "enter after this", no pulse required). Use Soundslice's syncpoint format for bars (`[bar, seconds, position-in-bar/480]`, https://www.soundslice.com/help/data-api/) so maps can move between the two tools. Also read and write Beat This/Sonic Visualiser `.beats` files.
2. **Local player.** Web Audio playback of a local file, a wavesurfer.js waveform, and pitch-preserving slowdown (Rubber Band compiled to WASM is used in-browser by https://github.com/creightonlinza/forever-jukebox). Slowing down must stretch the map's timings too.
3. **Map making in three passes.** First he taps downbeats by keyboard or foot pedal while listening, as in Soundslice and Transcribe!. Then Beat This! fills in the beats between his taps. Then he fixes errors, and each fix re-anchors the tracker from that point on, like Soundslice's "delete this and subsequent" (https://www.soundslice.com/help/en/creating/syncing/296/automatic-syncpoints/).
4. **Click, count-in and cues from the map.** Clicks are scheduled on the audio clock at the mapped beat times. The count-in uses the local beat spacing at the loop start. For rubato sections, a visual and audible cue fires before the entrance event. Loops are by bar, with an optional count-in before each pass.
5. **Synced chart.** Show his iReal-style or MusicXML chart and highlight the current bar. Reuse Blues Flow's chart code.

**Milestone test:** for each troublesome recording, he can (a) make or fix the map in under 10 minutes, (b) loop any 4 bars with a count-in and come in on beat 1, and (c) make every entrance out of a rubato section on the first or second try. Record pass or fail per tune.

**One step past the milestone: entrance feedback.** Record the microphone while he plays. Detect the first note onset after each cue or downbeat and report how many milliseconds early or late he was, per bar. This reuses the map, needs no new data, and is the first piece of "Brass coach that listens". The hard part is measuring the round-trip audio latency of his setup. Bluetooth headphones will break it.

## The hardest technical problem

The hard part is a correct beat and bar map for expressive jazz, made quickly. Neural trackers are good on steady music. They fail in exactly the cases David cares about:

- A 2026 failure analysis found tempo instability is "the dominant cause for beat prediction errors". Models trained on steady music produce "confident-but-wrong" output on expressive timing. Slow pieces get forced into double-time (https://arxiv.org/html/2605.12287v1).
- The Beat This! authors say their model inserts non-periodic beats on underrepresented material (https://arxiv.org/html/2407.21658).
- On jazz, trackers switch between metrical levels, such as half and double tempo (https://arxiv.org/html/2210.06817v1). Capo's own documentation says its downbeat finder can't handle odd or changing meters (https://supermegaultragroovy.com/products/capo/user-guide/latest/concepts/about-beat-tracking.html).
- Rubato intros have no beat at all, so no tracker can be "right" there. That is why cue events need to be a separate concept from beats.

So the work is in the interaction more than the model. Treat the tracker as a draft. Let a few human taps pin it down, and make each fix cheap and local. The playful research question is how few taps it takes. One promising lead: a tempo range taken from the taps is known to fix tracker continuity even when it doesn't fix exact beat placement (same 2026 paper).

A smaller technical risk is keeping clicks tight against stretched playback in the browser. That is solvable with careful audio-clock scheduling.

## Build vs extend

- **Extend (cheapest, try first):** Soundslice Plus for the player, plus a script that turns his iReal/MusicXML charts into Soundslice imports. Soundslice's code is closed, so its gaps can't be closed from outside except through its API, which needs the $20/mo Teacher plan.
- **Build (if Step 0 shows real gaps):** a small static app combining Beat This! in the browser, wavesurfer.js and Web Audio, with Soundslice-compatible maps. Scope it to the three gaps: rubato cues, owned map files and entrance feedback. Do not re-create Soundslice's notation editor.

## Sources

[1] https://www.soundslice.com/help/en/creating/syncing/171/adding-syncpoints/
[2] https://www.soundslice.com/help/en/creating/syncing/27/guide-notes/
[3] https://www.soundslice.com/help/en/creating/syncing/296/automatic-syncpoints/ ; https://www.soundslice.com/blog/312/new-see-detected-beats-when-editing-syncpoints/
[4] https://www.soundslice.com/help/en/creating/notations/95/bars/
[5] https://www.soundslice.com/blog/19/count-in-before-playback/
[6] https://www.soundslice.com/help/en/player/basic/8/metronome-and-count-in/
[7] https://www.soundslice.com/plans/
[8] https://www.soundslice.com/help/data-api/
[9] https://supermegaultragroovy.com/products/capo/user-guide/latest/concepts/about-beat-tracking.html
[10] https://supermegaultragroovy.com/products/capo/ios/ ; https://supermegaultragroovy.com/products/capo/mac/
[11] https://supermegaultragroovy.com/products/capo/
[12] https://supermegaultragroovy.com/products/capo/pricing/
[13] https://moises.ai/features/metronome-online/
[14] https://help.moises.ai/hc/en-us/articles/9570133423772-How-to-use-the-new-Chords-view-Grid-Mode
[15] https://moises.ai/blog/latest/improvements-latest-releases/
[16] https://help.moises.ai/hc/en-us/sections/8471545554716-Track-Separation
[17] https://moises.ai/blog/latest/moises-features/ ; https://moises.ai/
[18] https://anytune.zendesk.com/hc/en-us/articles/27099871079693-Count-In-and-other-Playback-Options
[19] https://develop.anytune.us/products/anytune-features/
[20] https://apps.apple.com/us/app/anytune-pro-studio-tools/id478293637
[21] https://www.seventhstring.com/xscribe/faq3.html
[22] https://seventhstring.com/xscribe/overview.html
[23] https://www.seventhstring.com/xscribe/buy.html
[24] https://www.ronimusic.com/manuals/ASD_Android_Manual.htm
[25] https://www.ronimusic.com/pricelist.htm
[26] https://www.irealpro.com/
[27] https://www.irealpro.com/learn/play-a-song/
[28] https://apps.apple.com/us/app/ireal-pro/id298206806
[29] https://support.chordify.net/hc/en-us/articles/360002148717-How-to-edit-chords
[30] https://support.chordify.net/hc/en-us/articles/360002148497-How-to-use-Chordify-on-Desktop
[31] https://chordify.net/premium ; https://support.chordify.net/hc/en-us/articles/360002164538-How-to-use-Premium-features
[32] https://www.vamp-plugins.org/plugin-doc/qm-vamp-plugins.html
[33] https://www.sonicvisualiser.org/doc/reference/5.2.1/en/
[34] https://jazzomat.hfm-weimar.de/tutorials/sv/sv_tutorial.html
[35] https://apps.apple.com/us/app/jazzbooks-streaming/id1667200133 ; https://streaming.jazzbooks.com/
[36] https://www.halleonard.com/feature/1209
[37] https://www.soundslice.com/help/en/creating/syncing/25/copying-syncpoints/
