# Moods: what makes a film feel cute, romantic, sincere, nostalgic or hype

A product film has a **tone** (`tones.md`): how it talks. A personal film, music edit or
memory montage has a **mood**: how it should make one specific person feel. The mood sets
every lever at once: pace, motion, transitions, type, colour, texture, words and sound.
Pick one mood per section. A film may travel between moods (cute → romantic → sincere),
but each section commits to its own.

**A mood mismatch is the fastest way to "faltu" (rubbish).** A girlfriend rejected an
apology film cut like a hype reel: glitch slices, flash frames, a cut on every beat. Hype
devices read as noise or aggression in a tender context, however well they're made.
When the user asks for energy that fights the purpose ("high energy" on an apology), say
so and propose a fit. Put the energy in the playful section, and keep the tender and
sincere parts slow.

## Choosing the mood
Ask, don't guess (`personal-films.md` §1):
1. **One word:** what should they feel at the end? Laugh · melt · forgive · nostalgic · proud · hyped.
2. **Their taste:** 1-3 reels they saved or shared, and what they'd find cringe.
3. **The footage:** motion-rich clips (dance, travel, sport) can carry hype. Mostly
   photos and selfies can't: they want cute, romantic or nostalgic treatments.

## Quick reference
| Mood | Shot length | Motion preset | Transitions | Grade (`GRADES`) | Type | SFX |
|---|---|---|---|---|---|---|
| Cute / playful | 0.6-1.5 s, reactions held 1-2 s | `bouncy` / `back` | pop cuts, sticker/doodle wipes, paper flips | `pastel` or `natural` bright | rounded + casual handwriting | dense, soft: pops, boops, squeaks |
| Romantic / tender | 2-5 s, the peak held longer | `smooth` / `expo` | dissolves 0.6-1.2 s, light leaks, match cuts | `warm` / `golden`, or `mono` | refined script or serif italic, sparse | almost none |
| Sincere / apology | the message decides; text 0.45 s/word + 1 s | `smooth`, near-still | cuts to black, slow fades | `natural`, gentle warmth | the sender's handwriting, or plain lowercase | none (voice or soft piano) |
| Nostalgic / memory lane | 1.5-3 s | `smooth`, handheld drift | film burn, flash-pop, page turn, gate weave | `faded` | date stamps, typewriter, captions | shutter, projector, tape hiss |
| Celebration | 0.5-2 s, bigger on drops | `snappy` / `bouncy` | pop, flash on the drop, zoom | bright `natural` | big friendly display | pops, cheers, confetti |
| Hype / velocity | 0.25-0.75 s, half beats on fills | `snappy` | whip, zoom cut, flash, speed ramps | contrasty `natural` or `digicam` | bold condensed caps | whooshes, impacts |
| Dreamy / aesthetic | 2-4 s, slow motion | `smooth` | soft blur dissolves, bloom | `pastel` / `faded` | small lowercase serif | sparkle, airy |
| Funny / meme | 0.3-2 s, deadpan holds | `snappy` / linear | hard cuts, freeze frames | `natural` | bold white with black stroke | record scratch, boing (sparingly) |
| Cinematic / epic | 2-4 s | `expo` / `smooth` | dramatic wipe, fade to black | teal-orange | wide-tracked caps, title cards | impacts, risers |

## The moods in detail
Each mood lists what it feels like, the levers, its signature moves, and what it never does.

### Cute / playful
*Feels like* a friend teasing you with stickers: small, round, bouncy, a bit silly.
- **Pace:** quick with bounce. Hold the funny face or reaction for 1-2 s: the hold is the joke.
- **Motion:** overshoot and settle. Scale pops 0 → 1.12 → 1, squash-and-stretch, wiggles
  (rotate ±4° twice), things that land. No long eased drifts.
- **Transitions:** a pop cut, a big doodle heart or sticker that fills the frame and
  clears, a paper flip.
- **Type:** rounded (Fredoka, Baloo 2, Nunito 800, Quicksand), or casual handwriting
  (Caveat, Patrick Hand, Gaegu). Lowercase; sticker text with a white outline (`StickerText`).
- **Colour:** bright natural or `pastel` grade. Pastel backgrounds: pink #ffd6e7,
  butter #fff1b8, mint #c9f2df, sky #cfe8ff, plus one saturated accent.
- **Texture:** doodles drawn over the footage (`Doodle`): a circle around a face, an arrow
  saying "this one", hearts popping on a smile, sparkles on a fit check. Photo-booth strips,
  sticker cut-outs, confetti on a laugh. Animate on twos (`useStepFrame(2)`) for a handmade wobble.
- **Words:** teasing, specific, in the couple's own slang ("bak-bak queen"), 1-4 words.
- **Sound:** soft pops, boops, a record scratch on a freeze frame. Playful music.
- **Signature moves:** freeze frame + doodle annotation ("caught being cute"); one quick
  reaction zoom on a funny face (a joke beat, not a camera punch); rating cards ("cuteness 11/10").
- **Never:** slow dissolves, heavy black vignettes, glitch, serious serif titles.

### Romantic / tender
*Feels like* being looked at by someone who adores you: slow, warm, close.
- **Pace:** slow, 2-5 s a shot. Let the smile finish. Cut on the look (eye contact) or
  on the exhale after a laugh. Cut faster only toward the song's peak, then hold long.
- **Motion:** slow push-ins of 3-6%, floats, slow motion (50-70%) on hair, turns and
  smiles. No bounce, no shake.
- **Transitions:** dissolves between images that share warmth or shape; a light leak or
  flare passing; match cuts (her smile → her smile years apart); a fade through warm white
  on the climax. Hard cuts only on the chorus beat.
- **Type:** sparing and airy, one short line at a time. Refined script: Great Vibes is
  everywhere, so prefer Pinyon Script, Allura or Parisienne. Or a warm serif italic:
  Cormorant Garamond, Playfair Display, Fraunces.
- **Colour:** `warm` or `golden` grade, soft contrast, slightly lifted blacks, warm skin.
  Black and white (`mono`) for timeless moments.
- **Texture:** fine grain, bloom on highlights, light leaks (`Leak`), bokeh, an optional letterbox.
- **Words:** second person, specific and quiet. "you laughed at your own joke for five
  minutes" beats "you are my everything".
- **Sound:** the song carries it. A camera shutter on a polaroid at most. The song's quiet
  parts are the film's pauses.
- **Signature moves:** close-ups of eyes, hands, hair; the "us" shot saved for the peak; a
  photo that comes alive as the clip from the same moment (moving polaroid).
- **Never:** glitch, RGB split, flash frames, fast whips, meme sounds, a cut on every beat, neon.

### Sincere / apology / heartfelt message
*Feels like* someone sitting across from you, being honest. **The message is the film.**
The visuals only support it.
- **Pace:** slow and still. Text holds 0.45 s per word, plus 1 s, and appears one thought at a time.
- **Motion:** almost none: a tiny drift, no effects.
- **Transitions:** cuts to black and slow fades. Silence is allowed.
- **Type:** the sender's own handwriting (photograph the note: `personal-films.md` §4),
  or a plain sans or serif in lowercase. No flourishes, no glow.
- **Colour:** natural, gently warm. Memories can be `mono`, the present in colour.
- **Words:** **the sender's own sentences, never song lyrics standing in for an apology.**
  Name the specific hurt, own it with no "if" and no "but", say what she means through
  specific memories, say what will change, and end with an invitation ("can we talk
  tonight?"), not a demand.
- **Sound:** their voice note is best, then soft piano, an instrumental, or silence.
- **Length:** 45-90 s. Longer starts to feel like a performance.
- **Never:** hype edits, trending templates, glitch, a cute sticker on the apology line,
  private photos used carelessly.

### Nostalgic / memory lane
*Feels like* flipping through a shoebox of photos.
- **Pace:** 1.5-3 s, roughly chronological. A quick montage can carry "all the middle months".
- **Motion:** polaroids dropping, a film strip running, page turns, a handheld camcorder drift.
- **Transitions:** film burn, flash-photo white pop, light leak, gate weave.
- **Type:** orange digicam date stamps (`Camcorder`), typewriter (Special Elite, Courier
  Prime), handwritten captions under polaroids.
- **Colour:** `faded` (lifted blacks, warm highlights, cool shadows); `mono` for the oldest.
- **Texture:** grain 0.08-0.12, vignette, frame borders, paper (`Paper`, `TapeStrip`).
- **Words:** dates, places and tiny captions ("first chai together · 12 jul").
- **Sound:** shutter clicks, a projector whirr, tape hiss under the music.
- **Never:** clean UI cards, neon, futuristic type.

### Celebration (birthday, anniversary, proud moments)
Bright and generous. Count-ups ("365 days of you"), a photo dump on the beat, big
friendly type, confetti and cheers on the drop. Cute in the middle, one tender hold at
the end (the wish, in the sender's words). Motion `snappy`/`bouncy`, transitions pop and flash
on the drop, bright grade, dense happy SFX.

### Hype / velocity
Fast. A cut every beat, half beats at peaks. Speed ramps go fast → slow on the hit → fast
(`scripts/speed_ramp.py`). Whips, zoom cuts and flashes on drops; element shake on
impacts; RGB split allowed. Bold condensed caps, a contrasty grade, whooshes and
impacts. **Needs motion-rich footage:** stills don't velocity. **Never** for apologies,
tender scenes, grief or anything a person will watch alone at night.

### Dreamy / aesthetic
Soft vibe edits: `pastel` or `faded`, slow motion, bloom and soft blur, small lowercase
serif text, a few sparkles, slowed-and-reverbed music. Restraint is the look: one effect,
lots of air.

### Funny / meme
Hard cuts, freeze frames, a punch-in on the reaction, deadpan holds, bold white captions
with a black outline, timing that waits half a beat before the punchline. Sound gags are
salt: one or two.

### Cinematic / epic
Letterbox, teal-orange grade, slow pushes, title cards, impacts and risers. See
`styles.md` (cinematic/documentary) and `camera.md`.

## Mixing moods along an arc
| Film | Arc |
|---|---|
| Love / apology (60-90 s) | cute 0-10 s (her quirks: remind her of the fun) → romantic 10-40 s (the moments) → sincere 40-80 s (his words, still) → invitation (one line, hold) |
| Birthday (30-60 s) | hook (her best laugh) → celebration photo dump with dates → cute bits → tender last shot + wish |
| Anniversary (45-90 s) | then vs now match cuts → counter of days → romantic peak on the "us" shot → message |
| Friendship / farewell | meme and cute all the way, one tender hold at the end |
| Personal brand / "more to me" | statement hook → hype montage of interests → calm sign-off |

## Turning a mood into tokens
- `theme.motion` from the table; `grain` 0.04-0.12 by mood.
- Fonts via `@remotion/google-fonts/<Name>` (check the exact names in
  `node_modules/@remotion/google-fonts/dist/esm`: `PinyonScript`, `Caveat`, `Fredoka`, `Baloo2`,
  `CormorantGaramond`, `SpecialElite`, …).
- Media grades: wrap clips and photos in `<Graded grade="warm">` (kit). Keep one grade per section.
- Kit pieces per mood: cute → `Doodle`, `StickerText`, `useStepFrame`; nostalgic →
  `Polaroid`, `Paper`, `TapeStrip`, `Camcorder`; romantic → `Leak`-style light, slow `Push`;
  hype → `scripts/speed_ramp.py`, `WhipIn`, `Flash`.
