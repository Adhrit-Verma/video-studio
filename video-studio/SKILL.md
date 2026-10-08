---
name: video-studio
description: Make videos in code with Remotion (React) in any style and tone - launch videos and short "brag" clips, teasers, promos and ads, feature explainers, demos, changelogs, pitch videos, brand films, animated infographics, and social clips for Reels, TikTok, Shorts, YouTube and LinkedIn. Analyzes the subject (codebase, repo, live website, docs), asks for purpose, focus, style, camera, tone and sound (or decides in quick mode), then builds 3D UI and infographic scenes with measured beat-sync or voiceover timing, CC0 sound effects and a finished mix, and delivers 16:9, 9:16, 1:1 and 4:5 exports with a poster frame and share caption. Use whenever the user wants any video, animation or motion graphic about an app, product, project, website, feature, company, event or idea, says "brag about this" or "make a launch video", wants a video synced to a song or voiceover, or wants a video re-cut, restyled, re-timed or made vertical - even if they never mention Remotion.
---

# Video studio

Make the video the user asks for, not a house style. This skill is a process and a
toolkit: **understand the subject → ask what the user wants → lock the look with style
frames → storyboard → build with the kit → finish the sound → review stills → render →
verify → deliver.** The catalogues in `references/` are vocabulary to offer the user,
not a template to copy.

## Principles (general, earned the hard way)
- **The user chooses style, camera, tone, focus and feel.** Offer concrete options with a
  recommendation; don't default silently to any one aesthetic. If they'd rather not
  choose, decide from the product and say what you chose (quick mode).
- **The hook is everything.** The first 2 seconds decide whether anyone keeps watching;
  plan the hook first. After one viewing a stranger knows what it is, who it's for and
  how to get it.
- **Be about the real thing.** Use the product's actual features, words and brand (from
  discovery); show the product *in use* (entry → key action → result) where the story
  lives. No abstract filler, no generic SaaS language.
- **Every scene earns a different technique.** Repeating one pattern (headline, then a
  panel, then a headline…) reads as a slideshow in any style.
- **Readable, not rushed.** Pace comes from motion and cuts; every line people read holds
  ~0.3 s per word (a label ~0.8 s) once settled. Fast in, then hold.
- **Camera smooth, elements on the beat.** The camera (pans, pushes, tracking) is always one
  continuous eased move: never kick-punched, stepped or shaken. The music drives element
  entrances (snapped to measured kicks) and scene transitions only. → `references/camera.md`
- **Camera smooth, elements on the beat.** The camera (pans, pushes, tracking) is always one
  continuous eased move: never kick-punched, stepped or shaken. The music drives element
  entrances (snapped to measured kicks) and scene transitions only. → `references/camera.md`
- **Timing is on a grid.** Entrances start on beats/8ths (or voiceover words), never
  on arbitrary fractions; with music, the grid is *measured*, the biggest moments sit on
  the strongest cues, and sync is verified on the rendered file.
- **Sound by default.** A music bed plus a few soft, well-timed effects mixed as one
  piece; silence only when chosen.
- **Look before rendering.** Style frames before building, contact sheets before every
  full render; stills cost seconds, renders minutes. Every frame should be postable.
- **Honest and private.** Only real features and true numbers; never the user's real
  data or any secret on screen; the user's own music rights.

## Workflow

### 1. Discover the subject
A project folder, a repo URL (clone it shallow into the scratchpad), a live website, or
other material. `python <skill>/scripts/discover.py <folder-or-url> --out brief`, then
read the README, the main UI files and the user flow it points to (or the rendered site
in a browser). Secret files are never read. Answer the planning rubric and write a short
product brief (pitch, audience, flow worth showing, ranked features, proof points, brand
tokens, assets, suggested tone, draft caption, gaps).
→ `references/discovery.md`

### 2. Brief: ask the user (or quick mode)
Two short rounds with options (use the structured question tool if available; up to 4
questions each, recommended option first):
- **Round 1:** purpose · focus (the flow and discovered features) + the one takeaway ·
  formats · length.
- **Round 2:** style direction · camera language · tone (sets copy voice, pacing,
  transitions, motion preset, SFX density) · sound (own track / generated beat /
  voiceover / silent; effects on) · end-card text and CTA.
**Quick mode:** when the user says "just make it", "/brag", gives only flags
(`--tone --format --duration --no-music --no-sfx --voice --title`), infer everything from
the rubric and state the choices in one message. If the user gives references ("like
X"), extract the traits and confirm them. Write the agreed creative brief to
`brief/brief.md`.
→ `references/brief.md`, `references/styles.md`, `references/camera.md`, `references/tones.md`

### 3. Scaffold
```bash
cp -r <skill>/assets/template <where-the-user-wants>/video && cd <that>/video && npm install
```
Set `src/theme.js` from the chosen style + brand (font, colours, surface, headline,
motion preset from the tone, grain). Timing lives in `video.json` (with music: its BPM;
voiceover or none: `bpm: 60` so units are seconds). Needs Node 18+, ffmpeg, Python with
numpy and Pillow. Keep the folder out of the product's git unless asked.

### 4. Style frames
Build 2-3 representative moments (a type scene, a UI scene, the end card) with the
theme, render them with `contact_sheet.py`, and show them. Adjust the theme until the
user likes the look. Cheap now, expensive later.

### 5. Sound and timing
- Music: own/library track → `analyze_music.py` (after looking at the track's
  structure); original → `gen_beat.py`. Track shorter than the story, or its calm and
  full parts in the wrong places? → `arrange_music.py` re-orders whole sections on the
  measured grid (video.json `arrangement`), but **never on the user's own song** unless
  they ask: a user rejected a re-arranged favourite ("don't do cuts on the songs, just
  match the story with the beat"). Fit the story to the song's own structure instead.
  Song longer than the film and the user OK'd an edit? → `edit_song.py`: `--map` (bars,
  sections, real drops), `--join OUT:IN` (seamlessness, want ≥ 0.93), then `--segments`
  with 1-2 joins builds the mastered edit + props (kicks measured on the edit itself).
  Otherwise `master_audio.py`: the master, per-frame `energy`/`bass` for audio-reactive
  visuals, and `out/cues.md` (the strongest beats).
- Voice-led films: `mix_voice.py` lays the voice lines over the uncut song, ducks the
  music under each one, adds a reverb tail after the last note and masters to -14 LUFS.
- Effects: choose from `<skill>/assets/sfx/` with `sfx-analysis.md` (low high-frequency
  risk for anything repeated), copy only those into `public/sfx/`, density by tone.
- Voiceover (only when asked): write for the ear, generate it first, fit scenes to it,
  duck the music.
→ `references/sound.md` (every sync failure mode and its fix, SFX mixing, cues)

### 6. Storyboard (show it as a table, get a yes)
One row per scene: time (beats or seconds) · what's on screen / said · technique ·
camera move · sound (cue lock, effects). The hook first; the flow as the centerpiece;
reveals on the strongest cues, drops or key words; pauses on gaps; the end card on the
calm part. A different technique per scene. Spell out what arrives one by one and what
interaction is simulated, and check every line's reading time against its hold.
→ `references/techniques.md`

### 7. Build
Scenes in `src/Video.jsx` using `src/kit.jsx` (all visuals read `theme.js`). Reuse the
product's real components where they render without a backend; otherwise mock UI as
components using the product's real labels; real screenshots only on invented data.
Place `<Sfx>` next to the visual it belongs to; `<Stream keys>` for typing. Branch layouts
per format as you go.
→ `references/css-3d.md` (kit API + rules that silently break 3D),
`references/formats.md`, `references/assets-and-honesty.md`

### 8. Review stills and self-check
`python <skill>/scripts/contact_sheet.py --comp Film --beats <one per scene, just after entrances, plus a few mid-transition>`
(and `--comp FilmTall --safe reels|tiktok|shorts` for tall). Check: cropped or
overlapping elements, contrast (AA), text in unsafe zones, two scenes that look alike,
muddy crossfades, anything off-brief. Then the checklist:
- the hook works in 2 s; the real product (ideally in use) is on screen;
- every read line holds long enough (no `[readability]` warnings in the render log);
- no `[layout]` warnings (text off the frame, a headline leaving one word on its last
  line): `contact_sheet.py` prints them, and the kit's `LayoutCheck` logs them in renders;
- 1-3 big moments sit on strong cues; sequential accents on the grid;
- effects are present, sparse and soft (unless the brief says otherwise); something
  breathes with the music when it fits the tone;
- the length matches the brief; the caption is drafted.
Fix, re-sheet the changed scenes.

### 9. Render, verify, finish
```bash
npx remotion render src/index.js Film out/film.mp4 [--props=out/props.json]
npx remotion render src/index.js FilmTall out/film-tall.mp4 [--props=out/props.json]
python <skill>/scripts/verify_sync.py out/film.mp4                   # with music
python <skill>/scripts/finish.py out/film.mp4 --beat <strongest settled moment>
```
Targets: net render offset within ±20 ms and no tempo drift (the script says IN SYNC or
prints the fix); -14 LUFS, ≤ -1 dBTP (`finish.py` re-normalizes the final mix if the
effects pushed it off); the poster is a settled, postable frame, baked in as frame 0.
Don't overwrite a render the user already has: version the names (`film-v2.mp4`).

### 10. Deliver and iterate
Write `out/share-copy.txt` (1-3 sentences in the tone, postable as-is; variants go in
`out/share-copy-variants.md`). Send the file(s) and the poster. Report in plain words:
scene list, what the sound does where, measured sync/loudness, file locations, how to
re-render, posting notes for social (upload the poster as the custom thumbnail).
Offer to re-roll a scene or try another tone.
On feedback: restate the problem in the user's terms, change only the named scenes,
re-sheet, re-render. When the user rejects a direction (e.g. a style or a 3D treatment),
record why in `brief/brief.md` so it isn't repeated.

## Optional: photoreal product shots
Blender, headless, for devices/objects (not UI, rarely type). Needs the user's OK to
install. → `references/blender.md`, `scripts/blender_product_shot.py`

## Practical traps
- Shell heredocs mangle code with quotes, `$` and backslashes: write files with the
  file tool, then run them.
- Background jobs may stop around 10 minutes: render long jobs (Blender, long films) in
  chunks and resume.
- On Windows, call `npx`/`node` through a shell from Python (`shell=True`).
- A still of an element that fades in exactly on beat n shows nothing at frame n:
  sample a little after.
- An `<Sfx>` inside a scene stops at the scene's end: give ringing tails room.
- Don't push render settings on laptops: `--concurrency` well above the default plus
  `--gl=angle` crashed a 16-thread / 15 GB machine outright. Keep the default concurrency,
  no GPU flags, and ask before any benchmark. Iterate with contact sheets,
  `--frames=a-b` scene renders and `--scale=0.5` drafts; render full-res once at the end.
- `CameraMotionBlur` renders its subtree once per sample (6 samples = 6× the cost of
  that scene): keep it to short, fast moves.

## Files
- `assets/template/`: Remotion project (`video.json`, `src/theme.js`, `src/kit.jsx`,
  placeholder `src/Video.jsx`, `src/Root.jsx` with 16:9 / 9:16 / 1:1 / 4:5,
  `tools/stills.mjs`).
- `assets/sfx/`: CC0 sound effects (impact, interface, ui, casino, keyboard) with
  `sfx-analysis.md/json` (brightness, high-frequency risk, suggested uses).
- `scripts/`: `discover.py`, `analyze_music.py`, `edit_song.py`, `arrange_music.py`, `gen_beat.py`, `master_audio.py`,
  `verify_sync.py`, `contact_sheet.py`, `finish.py`, `blender_product_shot.py` (usage in
  each docstring).
- `references/`: `discovery.md`, `brief.md`, `styles.md`, `camera.md`, `tones.md`,
  `techniques.md`, `sound.md`, `css-3d.md`, `formats.md`, `blender.md`,
  `assets-and-honesty.md`.
