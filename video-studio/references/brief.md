# The brief: ask the user what they want, with options

The user decides the style, camera, focus, tone and feel. Your job is to make those
choices easy: short questions, concrete options (with a one-line description of what
each looks like), a recommended default, and nothing asked that the discovery already
answered.

## Quick mode: when the user doesn't want questions
If the user says "just make it", "you decide", "/brag this", gives only flags, or asks
for a quick clip, skip the rounds: answer the planning rubric (discovery.md §5) yourself,
choose purpose, tone, style, camera, format, length and sound from it, and state the
choices in one short message before building ("Tone: yc-parody, 'fake Series A launch';
16:9, 20 s; clean light in the product's colours; generated beat plus soft UI sounds").
Still show the style frames and the storyboard, which are cheap to change.
Options may arrive as flags or plain words; treat both the same:

| Option | Values | Default |
|---|---|---|
| `--tone` | a preset (tones.md) or freeform direction | inferred from the product |
| `--format` | `landscape`/`wide` 16:9, `vertical`/`tall` 9:16, `square` 1:1, `portrait` 4:5 | landscape |
| `--duration` | seconds | purpose default (a social brag ~20 s) |
| `--style` | a family from styles.md | the product's own system |
| `--no-music`, `--no-sfx` | flags | music and effects on |
| `--voice` | flag | no voiceover |
| `--title` | string | the product's name |

## How to ask (the full brief)
- Use the structured question tool if available (e.g. `AskUserQuestion`): up to 4
  questions per call, 2-4 options each, "Other" is always available for free text.
  Mark your recommendation first with "(Recommended)", based on the product brief.
- Two rounds at most: **Round 1** purpose/focus/format/length; **Round 2** style, camera,
  tone, sound. Motion feel follows from the tone and style (tones.md); ask about it only
  when they pull in different directions. Then confirm the creative brief in one message.
- Offer previews when choosing a look: after round 2, render 2-3 **style frames**
  (stills of one scene in the chosen style) and let the user react before building.
- If the user gave references ("like the Apple Vision Pro reveal", "like a Linear
  changelog", a video link), extract the traits (palette, pace, camera, type, music) and
  confirm them back instead of re-asking.

## Round 1: what and for whom
1. **Purpose:** social brag / launch clip · launch teaser · feature explainer · social ad ·
   product demo walkthrough · update or changelog · investor or pitch video · tutorial ·
   brand film · event promo.
2. **Focus:** which features or moments must be in it (multi-select from the discovered
   features, the flow first, ranked by how visual they are); what the ONE takeaway is.
3. **Formats:** 16:9 (YouTube, site, pitch), 9:16 (Reels/TikTok/Shorts/Stories), 1:1
   (feeds), 4:5 (Instagram feed). Multiple is fine: the kit re-lays out per format.
4. **Length:** 15-25 s (brag/hook/ad), 20-40 s (teaser), 45-90 s (explainer), 2-3 min (demo).

## Round 2: how it looks, talks, moves and sounds
5. **Style direction** (see `references/styles.md` for the full menu):
   keynote dark · clean light · bold kinetic typography · playful/rounded · glassmorphism ·
   editorial/serif · retro/VHS · neon/cyber · cinematic/documentary · isometric/illustrative ·
   brutalist · the product's own brand system (default when the brand is strong).
6. **Camera language** (see `references/camera.md`): static and graphic · slow push/drift ·
   orbit and fly-through (3D) · isometric/top-down diagrams · whip pans and fast cuts ·
   handheld/documentary · parallax layers.
7. **Tone** (see `references/tones.md`): default (playful, clean) · polished (serious,
   elegant) · yc-parody (deadpan startup launch) · chaotic (fast, loud) · deadpan (calm,
   dry) · cinematic (trailer-scale) · app-store (clean feature cards) · or freeform
   direction. It sets copy voice, pacing, transitions, SFX density and the motion preset
   (calm and premium `expo` · crisp `snappy` · playful `bouncy`/`back` · cinematic
   `smooth` · mechanical `linear`).
8. **Sound:** their own track (they put the file in `public/`) · an original generated beat
   (genre + tempo) · voiceover (they record, or local TTS) · music + voiceover · silent
   with captions. Effects on by default (soft, under the music); say so. For music:
   cut to the beat or loosely?
9. **Brand assets & text:** logo/wordmark to use, colours to keep, words to avoid,
   call to action and URL for the end card, on-screen text density (minimal ↔ explanatory).
10. **Honesty/privacy constraints:** real screenshots allowed? (only on invented data),
    claims that must be verifiable, anything confidential.

## The creative brief (confirm before building)
```
Purpose / audience: ...
Formats / length: 16:9 + 9:16, ~40 s (N beats at X BPM)
Focus: 1. ... 2. ... 3. ...   One takeaway: "..."   Flow shown: entry → action → result
Hook (first 2 s): ...
Tone: <preset> - "<freeform direction>"; motion feel: <preset>
Style: <family> - palette ..., type ..., surfaces ..., background ...
Camera: <language>
Sound: <music/VO plan>; sync: <tight on kicks / loose>; cue locks: <which moments>;
       effects: <palette and density>; audio-reactive: <none/subtle, which element>
End card: <wordmark>, "<CTA>", <url>
Share caption (draft): "..."
Scenes: see storyboard table
```
Write it to `brief/brief.md` so later iterations (and later sessions) stay consistent.
