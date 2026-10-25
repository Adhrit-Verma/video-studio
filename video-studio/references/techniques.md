# Storyboarding and the technique catalogue

## Contents
1. Timing units: beats or seconds
2. Story shapes by purpose
3. Creative laws
4. What to show (the product in use first)
5. Techniques by job (pick a different one for each scene)
6. Copy
7. Readability: pace without losing the text
8. Rhythm rules
9. Transitions

---

## 1. Timing units: beats or seconds

Scenes, entrances and exits are numbers on one grid (`video.json` → `bpm`):
- **With music:** 1 unit = 1 beat of the measured grid. Cuts land on the music, and
  the film re-times itself if the track changes. 1 bar = 4 beats; scenes of 4/8 beats.
- **Voiceover or no music:** set `bpm: 60`, so 1 unit = 1 second; align scenes to
  voiceover sentence start times.
`frames = unit * fps * 60 / bpm`.

Put story on the music's structure (measure it: `references/sound.md`): the brand or
main reveal on a drop or one of the strongest cues (`out/cues.md`), a pause on a gap,
the end card on a calm outro.

## 2. Story shapes by purpose

| Purpose | Shape |
|---|---|
| Social brag / launch clip (15-25 s) | hook (2-3 s) → reveal (2-4 s) → 2-3 sharp highlights, ideally the product in use (5-12 s) → punchline/outro (2-4 s). 18-22 s is the sweet spot |
| Launch teaser (20-60 s) | hook → tension/build → **reveal** (name/product) → 2-6 feature beats → proof/trust → end card |
| Feature explainer (45-90 s) | the problem as a question → how it works (diagram) → the feature working in real UI → a second example → limits/proof → CTA |
| Social ad (10-20 s) | payoff in the first 1.5 s → one feature → brand + CTA; the first frame must already be interesting |
| Demo walkthrough | follow one real task end to end; each step its own scene; show inputs and results |
| Update / changelog | "New in X" → one card per change (4-8 beats each, each a different technique) → CTA |
| Pitch / investor | problem → insight → product → traction numbers → team/vision → ask |
| Brand film | mood → people/story → product as the enabler → line → logo |
| Tutorial | goal → steps with UI close-ups and callouts → result → where to learn more |

Shapes are starting points: not every product needs three highlights. The tone
(`tones.md`) sets the scene count and pacing within a shape.

## 3. Creative laws
These hold in every style and tone.
- **The hook is everything.** The first 2 seconds decide whether anyone keeps watching.
  Plan the hook before anything else; the first frame is already interesting.
- **Clear to a stranger.** After one viewing, someone who has never heard of it knows
  what it does, who it's for, and how to get it. Lead with that, not with how it's built,
  unless the brief is about how it's built.
- **Show the thing.** At least one scene shows the real UI, copy or key visual. No
  abstract filler (colour washes, generic particles, stock "intelligence" graphics).
- **Specific.** It must feel made for this exact project: its own copy, claims, colours.
- **No generic SaaS language.** Banned: "streamline your workflow", "elevate", "supercharge",
  "unlock", "seamless", "next-level", "game-changer", "excited to share".
- **Readable** (section 7). Pace comes from motion and cuts, never from pulling text away early.
- **Make it alive.** Things arriving one by one, simulated clicks, swipes and typing beat
  static slides.
- **Funny earns its place.** Humour comes from the project's own absurdity, not from trying.
- **Every frame postable.** Any frozen frame should be worth sharing (the poster is one).
- **Short.** Every second has a reason; cut the scene that doesn't.

## 4. What to show (the product in use first)
If discovery found a flow (entry → key action → result), the **centerpiece scenes show
that flow**. The product *doing* its thing beats the product *describing* its thing.
In order of preference:
1. **A working-app moment**, rebuilt from the real routes/components: the upload screen
   with a file dropping in, the result view, a dashboard with realistic invented content.
2. **One real UI element**: a hero card, the swipe UI, a progress meter, a stat block.
3. **The core concept animated**, grounded in the idea (taxis for taxis: a taxi inside a taxi).
4. **Text-forward**, when the product is copy-driven: the copy is the visual.
Diagrams of what the product does, and the landing page's stat row, still have a place,
but at most one of them, framing the flow rather than replacing it.

**Commit to sequences and interactions in the storyboard.** Before writing it, ask what
can appear one by one (cards, stats, list rows, results) and what can be simulated
(click, swipe, type, toggle). Write it into the scene: "3 profiles slide in one by one,
each with a card sound", "the cursor clicks Export", "the hook types itself with key
ticks". Vague scenes become static slides.

## 5. Techniques by job

Variety is the rule: within one film, don't reuse a technique for two scenes unless it
is deliberate (a recurring motif). All are CSS-3D and kit pieces; adapt colours and
motion to the chosen style.

**Hook (grab attention)**
- *Wall of things* - a curved wall of cards/pages/photos (x = sin a·R, z = -cos a·R + R) that falls away on a beat: abundance → loss.
- *Question barrage* - one short question per beat over a moving background (short enough to read at that pace).
- *Cold open on the payoff* - start on the most impressive frame, then rewind ("here's how").
- *Type slam* - one huge word per beat filling the frame (kinetic styles).
- *The problem, stated straight* - one serious line the product answers (yc-parody, deadpan).

**Build tension (before a reveal)**
- *Tunnel / fly-through* - objects rush past the camera, accelerating; flash into the reveal.
- *Countdown / stacking* - elements stack or count toward a number.
- *Silence* - cut the visuals to near-empty when the music drops out; land words on the music's small hits.

**Reveal (name, product, feature)**
- *Wordmark slam* - scale + blur-in on the drop, a flash, a glow that breathes with the music.
- *Device/hero reveal* - product rises into light (Blender or CSS), camera settles.
- *Mask wipe* - the name revealed by a moving shape or line.
- *Assemble* - pieces fly in and lock into the logo/UI.

**Explain (how it works)**
- *Exploded view → assemble* - UI layers apart in depth with labelled callouts, then snap into the real UI.
- *Pipeline / stack* - isometric plates or boxes; data dots flow through; blocked items bounce off a layer.
- *Parse into cards* - a sentence/request; key words light up and fly into labelled cards (what/when/where).
- *Before → after split* - two layers in depth, one gives way to the other.
- *Flowchart build* - nodes appear and connect on the beat; a pulse travels the path.
- *Map / network* - points light up and connect.

**Demonstrate (it works)**
- *Tilted screen + live UI* - a page/device plane in perspective; UI layers above it (parallax); a cursor or waveform drives it.
- *Filmstrip + scanner* - items slide past a beam; matches get tagged; rewind and lift the best one.
- *Typewriter answer* - results stream in word by word (`Stream`, with `keys` for key ticks).
- *Card flip + dive* - a card flips in, the camera dives into a detail, an outline draws around it.
- *Cursor choreography* - a fake cursor clicks through a flow; ripples and click sounds on clicks.
- *Swipe / drag* - a card follows a gesture off-screen, the next one settles (card-slide sound).
- *Picture-in-picture* - the phone and the laptop showing the same thing.

**Prove (trust, numbers, limits)**
- *Counters / stat tiles* - numbers count up with `Count`, one hero number in the accent.
- *Timeline infographic* - a floor-tilted track with ticks; a playhead sweeps; cards stand up at the moments that matter.
- *Big type + object* - a fact word by word beside a 3D card (calendar, chart, badge).
- *Comparison* - bars or columns growing; the product's one highlighted.
- *Quote / testimonial card* - a real quote only, with attribution.

**Close**
- *End card* - wordmark, one-line promise, CTA, URL; hold 4-8 beats; fade over the last 1.5.
- *Punchline* - the last line lands, a beat of silence, then the name.
- *Hero shot finale* - a slow orbit of the product beside the wordmark.
- *Loop back* - end on the opening image, resolved.

## 6. Copy
- One idea per scene; headlines ≤ 6 words; captions ≤ 10.
- Use the product's real vocabulary (from discovery), and the viewer's language ("you").
  The tone sets the voice (tones.md).
- Pair a plain line with an accented payoff: "Set it once. *It remembers.*"
- Questions build tension; statements resolve it.
- Never imply features that don't exist (an illustration is fine; UI that looks like a
  feature is a promise). Numbers must be true. Small illustrative UI text is fine (a
  filename, an "Exported" toast); invented claims, stats or testimonials are not.

## 7. Readability: pace without losing the text
Every line the viewer is meant to read stays **fully visible and settled** (entered, not
yet leaving) long enough to read it, counted from when the whole line is on screen:
- a label or 1-3 words: about **0.8 s**;
- a headline or sentence: about **0.3 s per word**, at least **1.2 s**; the hook gets the most.
Fast in, then hold; never fast in, then gone. The kit's `useReadBeats(text)` converts this to
beats at the current tempo (`readSeconds(text)` gives seconds), and `Words` warns in the render log when its `out` comes too
early. Text that is only texture (a scrolling code wall) needn't be read.

These are floors for fast social cuts. For explainers and story films, use about
**0.45 s per word**: a viewer who rejected a 91 s, 21-scene cut at 0.3 s/word called it
"too fast, no time to process text". **UI text the viewer must read counts too**: an
answer panel or card needs its own hold once it has finished streaming. Keep in-UI copy
short (≤ 10 words) so it can be held.

**More than ~10 features? Tell a story, not a list.** Give it a protagonist, stakes and
time that visibly passes, and let each feature appear because the story needs it.
Make time explicit: a chapter card in words ("SUNDAY · 11:40 AM", with AM/PM, the clock
rolling on from the last chapter, and one plain line of what's happening), then a small
persistent clock. Bare numerals ("13:31") flashing between scenes were "hard to
understand".

Design these out at the storyboard stage:
- **Too much text for the scene.** A 4 s scene lands 2-3 short reads, not 6. Cut copy
  or split the scene; don't speed it up.
- **Sequential text on a fast grid.** At 110+ BPM beats are ~0.5 s apart: fine for dots,
  ticks and glows, too fast for lines people read. Reveal text on every other beat, or
  reveal the set quickly and hold it all on screen. Note each sequential text reveal's
  hold in the storyboard.

Contrast: body text ≥ 4.5:1 against what's behind it, large text ≥ 3:1 (WCAG AA). Check
it on every background a caption crosses; add a chip or scrim when it fails.

## 8. Rhythm rules
- Cutting real footage? Emotion outranks rhythm: let the smile finish, cut on the action or
  the look, and vary shot lengths (`editing.md`). The grid places cuts; it doesn't choose shots.
- Entrances start on a beat or an 8th (x.0 / x.5) or on a VO word; never at arbitrary
  fractions. Fractional starts read as "not synced" even when scene cuts are on the grid.
- Fast attack, slow settle (the chosen motion preset); the *start* of a motion is the hit.
- Camera punch on measured kicks only in energetic sections; none in intros, silences
  and outros.
- Cut rate follows energy: 1 per 8 beats when calm, 1 per beat in builds, 8ths just
  before a drop (visuals, not reading text).
- Flashes only on drops and slams.
- End card: hold at least 4 beats, fade the last 1.5.

## 9. Transitions
Match them to the tone (`tones.md`): hard cuts for yc-parody and chaotic, slow dips for
polished and deadpan, slides and wipes for app-store, dramatic wipes for cinematic.
- A plain crossfade between two busy layouts is a muddy double exposure. Stagger it (the
  old content leaves, then the new content enters) or dip through the background colour
  (`Cover` at the start of the new scene).
- Review stills mid-transition as well as settled (`contact_sheet.py --beats` a quarter
  beat either side of a cut).
