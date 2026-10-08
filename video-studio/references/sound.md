# Sound: music, effects, voiceover, sync and the finish

## Contents
1. Options (and rights)
2. Pipelines
3. Reading a track's structure
4. Why sync fails, and the fixes
5. Mastering: a smooth finish
6. Voiceover
7. Verifying
8. Strong cues: where the big moments land
9. Sound effects
10. Audio-reactive visuals

Default posture: **include sound.** One tasteful music bed plus a few well-timed effects
almost always beats silence. Go silent only when the user asks, when the brief makes
silence the joke, or when the video will only autoplay muted (then captions carry it).

---

## 1. Options (and rights)

| Option | When | Notes |
|---|---|---|
| **User's own track** | they have a song in mind | they put the file in `public/`; never download commercial music; say once that posting a copyrighted track can get the video muted/claimed, and offer the in-app music route for Reels/TikTok (mute the file's audio, add the song in-app from the printed offset) |
| **Original generated beat** | safe-to-post music in a genre | `gen_beat.py --style phonk\|minimal`, arranged on `video.json`; exact kick times come with it. For other genres, extend the script's instruments or ask the user for a royalty-free track |
| **Royalty-free library track** | the user has one (licence in hand) | same pipeline as own track |
| **Voiceover** | explainers, demos, pitches | only when asked; time scenes to sentences (bpm 60); music ducked under the voice |
| **Silent + captions** | feeds that autoplay muted | captions carry the story; still consider a soft bed |
| **Sound effects** | nearly always, on top of the above | CC0 library in `assets/sfx/` (section 9) |

Tempo guide: 70-95 BPM calm/cinematic; 100-125 confident product; 128-150 hype/ads.

## 2. Pipelines
```
own/library track: analyze_music.py public/song.mp3 --drop <s> --bpm <rough> -> out/sync.json
original beat:     gen_beat.py [--style ...]                                 -> public/beat.wav + out/sync.json
music, both cases: master_audio.py                -> public/<x>_master.wav + out/props.json + out/cues.md
effects:           copy the chosen files from <skill>/assets/sfx/ to public/sfx/; place them with <Sfx>
render with props: npx remotion render src/index.js Film out/film.mp4 --props=out/props.json
verify:            verify_sync.py out/film.mp4
finish:            finish.py out/film.mp4 --beat <poster beat>   (final loudness, poster as frame 0)
```
`video.json` keys used: `bpm`, `totalBeats`, `dropBeat`, `introBeats`, `breaks`,
`endBeat`, `punch`, `nudge`. `props.json` also carries per-frame `energy` and `bass`
(0..1) for audio-reactive visuals; `cues.md` ranks the grid beats by intensity.

## 3. Reading a track's structure
Before storyboarding, look at the song: print mean loudness per second, then per beat
around interesting spots (a few lines of numpy over ffmpeg-decoded audio). Look for:
- the **drop** (loudness jump; its downbeat, not the loudest transient before it);
- **gaps** (near-silence) and the small hits inside them: perfect for a pause or a twist;
- a **second drop**: a second reveal;
- a **calm outro**: the end card.
Then set `dropBeat`, `breaks`, `endBeat` and story beats on them. After mastering,
`out/cues.md` lists the strongest beats (section 8).

## 4. Why sync fails, and the fixes
| Symptom | Cause | Fix |
|---|---|---|
| cuts drift later and later | guessed tempo (e.g. 115 vs a real 115.54 ≈ 50 ms by the end) | measure tempo from kick-phase drift (analyze_music.py) |
| everything a hair early | anchored to a pickup transient instead of the downbeat | the drop = the grid beat nearest the rough mark |
| the grid fit wobbles | full-band onsets; snares/hats flip on/off-beat per section | fit on the kick band (30-120 Hz) only |
| a long window breaks the fit | a quiet section with off-beat kicks | outlier rejection (drop worst window, refit) |
| perfect in the WAV, late in the MP4 | AAC encoder priming (~42 ms) | `nudge` (0.026 measured with Remotion 4), check with verify_sync.py |
| "feels unsynced" though cuts measure fine | entrances at fractional beats, floaty easing | entrances on beats/8ths, fast attack, punch on real kicks |
| text feels rushed on a fast track | a new line on every beat at 110+ BPM (~0.5 s apart) | text on every other beat, or reveal fast and hold the set (techniques.md → Readability) |

## 5. Mastering: a smooth finish
`master_audio.py` shapes the track around the story:
- **intro:** 1-beat fade-in, muffled until `introBeats` (anticipation). Set 0 to skip.
- **breaks:** dip and muffle, then slam back on the break's last beat (5 ms ramp, no
  click). Skip when the song has its own gap.
- **end:** a sub impact on `endBeat`, low-pass sweep, warm reverb tail to silence.
- **loudness:** -14 LUFS, -1 dBTP (streaming norm); two-pass loudnorm.
- One continuous filter, no splices (splices click). Look at the spectrogram of a new
  master: `ffmpeg -i m.wav -lavfi showspectrumpic=s=1200x360:legend=0:scale=log out/spec.png`.
Taste varies: a lo-fi or cinematic brief may want no impact and a long fade; edit the
curves in the script rather than fighting them.
Effects are mixed by Remotion on top of the master, so the final mix can drift from the
target: `finish.py` measures the rendered file and re-normalizes it when needed.

## 6. Voiceover
Opt-in only: never add narration the user didn't ask for.
- **Write it for the ear.** Narration complements the visuals; it doesn't read the text
  on screen aloud. Make it conversational, specific to the product and concise, matched to
  the scene pacing, with smooth hand-offs between scenes. Put the script in `brief/brief.md`.
- The user records (best), or local TTS: Kokoro (`pip install kokoro soundfile`; voice
  `af_heart` is a good default; natural and offline) or, for rough drafts on Windows,
  PowerShell `System.Speech.Synthesis.SpeechSynthesizer` → WAV. Paid neural TTS only with
  the user's own key.
- **Let the voice set the pace.** Generate the VO first, measure it, then fit scene
  lengths to it rather than squeezing speech into pre-set scenes.
- Get sentence start times (e.g. faster-whisper with word timestamps) and put scene
  boundaries and key entrances on them; `bpm: 60` makes units seconds.
- Duck music under speech (-12 to -18 dB, i.e. to about 0.12-0.25 of its level) with
  ffmpeg `sidechaincompress` or a volume curve; normalize the final mix to -14 LUFS.
- Burn in captions for social (Remotion text, synced to the word timestamps).

## 7. Verifying
`verify_sync.py out/film.mp4` checks the rendered file two ways:
- **render offset** (exact): cross-correlates the rendered audio with the master WAV;
  the AAC encoder measured +43 ms here, and `nudge` 0.026 leaves a net +17 ms: fine.
  If the net exceeds ±20 ms, set `nudge` to the measured shift and re-master.
- **grid check**: expected kicks vs onsets in the analysis band (30-120 Hz, so the
  detector's bias cancels): median, spread, drift across quarters. Drift = wrong tempo.
  A well-synced song cut measured -6 ms median, 12 ms IQR, 3 ms drift. Generated beats
  are exact by construction; their grid check is only informational.
Run it before `finish.py` (effects add onsets, but the offset check still holds).
Report the numbers to the user; "synced" without a measurement is a guess.

## 8. Strong cues: where the big moments land
`master_audio.py` scores every grid beat of the master: 0.45 × onset strength + 0.25 ×
local onset contrast + 0.20 × loudness (RMS) + 0.10 × bass energy, each normalized per
track. `out/cues.md` lists the strongest beats (beat number and seconds) and the whole
grid's intensities.
- Put the **1-3 biggest moments** (the name reveal, the payoff, the logo) on the
  strongest cues near where the story wants them. Several locks in a 20 s film start to
  feel mechanical.
- Put **sequential accents** (dots, ticks, glows, non-text pops) on consecutive beats.
- **Readability wins.** Ignore a cue when it rushes copy, breaks scene pacing or the
  product story. Quiet tones (deadpan, yc-parody) use cues rarely, maybe only for the logo.
- Mark the lock in code so later edits keep it: `{/* cue-lock: beat 24 (strongest) */}`.

## 9. Sound effects
The library (`<skill>/assets/sfx/`, all CC0, credits in its README):
`impact/` (soft thuds, bells, wood, plates, glass, punches), `interface/` (clicks, drops,
switches, bong, glitch, error), `ui/` (clicks, mouse click, rollovers, switch variants),
`casino/` (card slides/places/fans, chips, dice, pack opening), `keyboard/`
(32 single keypresses). **Read `sfx-analysis.md` before choosing**: it ranks files by
high-frequency risk (hissy, clicky, fatiguing when repeated) and lists safe picks per use.

Copy only what you use into the project (`public/sfx/<family>/`), then place it in the
scene next to the visual it belongs to; timing is in the scene's beats:
```jsx
<Sfx at={0} src="sfx/impact/impactSoft_medium_001.ogg" volume={0.5} />   {/* the reveal */}
<Stream text="Write the lesson here" at={2} step={0.25} keys />              {/* a keypress per word */}
```

**Moment → sound**
| Moment | Families | Notes |
|---|---|---|
| Cards/items arriving in sequence | `casino/card-slide-*`, `card-place-*`, `card-fan-*`, `interface/drop_*` | match the gesture; in dense runs accent only the first, last or strongest item |
| Big reveal / payoff | `impact/impactSoft_medium_*` (safest), `impactBell_heavy_000/003/004`, `interface/bong_001` | one short announcement cue as it lands |
| Typed text | `keyboard/keypress-*` (randomized), `interface/drop_*` | `<Stream keys>`; thin out or skip when copy is dense |
| Simulated clicks, taps, toggles | `interface/click_*`, `select_008`, `switch_*`, `ui/mouseclick1` | on the press, matching the visible action |
| Success / completion | `impactBell_heavy_*`, `casino/chips-collide-*` | when the metric or result is fully visible |
| Counter ticking up | `casino/chips-stack-*` | a few, not one per number |
| Chaotic or comedic beat | `interface/glitch_*`, `error_005/006`, `impactPunch_heavy_*`, `casino/dice-throw-*` | only in tones that can take it |

**Density by tone** (tones.md): polished 2-3 soft cues · default 3-5 · yc-parody 2-3 dry
cues · app-store a light, even layer (one per feature card) · cinematic 2-3 big hits ·
deadpan 1-2 · chaotic dense, on beats, stacked.

**Timing:** a sound starts with the gesture (clicks at the press, entrances 0-0.1 beat
before the first visible frame); reveal and success sounds land with the payoff; a
transition sound at the transition start.

**Mix it as one piece, not stickers on top.** Effects sit softly under the music:
- volumes against a -14 LUFS master: reveals/impacts 0.35-0.6, clicks and drops
  0.25-0.45, keypresses 0.12-0.25, repeated small sounds at the low end;
- prefer low/medium HF-risk files for anything repeated or for polished tones; bright
  files only as tiny, quiet, isolated accents;
- one coherent sonic palette per film (e.g. soft impacts + interface drops), not a grab bag;
- fewer cues with better timing beat many. An effect inside a scene is cut at the
  scene's end, so give a ringing tail room or place it at the film level.

## 10. Audio-reactive visuals
Beat sync decides *when* things happen; audio-reactivity lets existing visuals *breathe*
with the music. `master_audio.py` writes per-frame `energy` (loudness) and `bass` to the
props; `useEnergy()` in the kit reads them, and `Glow` already breathes with them.
- **Good targets:** a hero glow or background warmth, the presence of a product card,
  a soft light on the title or logo at strong moments, vignette/depth.
- **Avoid:** waveform or equalizer bars, musical-note graphics, particle visualizers,
  strobing, heavy pulsing, text that scales and hurts readability.
- Keep it subtle (a 5-15% swing) and skip it for deadpan/stillness briefs.
