# Editing real footage: choosing moments and cutting with feeling

Product films are built shot by shot in code. Personal films, music edits and montages are
**cut from footage**: phone clips, photos and screen recordings. That's a different craft.
The most common failure is mechanical: a shot list generated on the beat grid that rotates
through clips by cursor. It lands on blurry frames, legs and floors, and on smiles cut in
half, and it reads as "a machine made this".

## 1. Emotion first
Walter Murch's Rule of Six (*In the Blink of an Eye*) ranks what a cut must serve:
**emotion 51% · story 23% · rhythm 10% · eye-trace 7% · 2D screen plane 5% · 3D space 4%**.
Give up the lower ones first. Rhythm is third: a cut on the beat that chops a smile in
half is wrong. A cut half a beat late that lets the smile finish is right, or slide the
shot so its moment lands on the beat.

## 2. Log before you cut
1. `python <skill>/scripts/clip_moments.py <media folder> --out out/moments` scores every
   clip (sharpness, steadiness, exposure, a person-in-frame estimate), flags duplicate
   photos, and writes numbered contact sheets of candidate moments.
2. **Look at the sheets.** The score only shortlists; your eyes pick. Faces, expressions and
   meaning are judged by looking.
3. Write a **shot log** in `brief/shots.md`: id · source · in-out · what happens · emotion ·
   where it goes. Every shot in the film comes from the log. **Never auto-assign footage
   by cycling through clips.**
4. Mark the 3-6 **money moments**: the laugh peak, the look into the lens, the hair flip,
   the "us" shot. They go on the strongest musical moments and get the longest holds.

## 3. What makes a good moment
- **Use:** the face visible and sharp; an expression at its peak (the widest smile, the
  beat after a laugh); eye contact with the lens; a complete gesture (start, apex, end);
  good light; a moment that shows who they are.
- **Reject:** blur and camera whips; mid-blink and mid-chew; accidental frames (floor,
  legs, pocket, ceiling); unflattering angles; faces cropped by our own zoom or panel;
  duplicate photos; long stretches of nothing. Text baked in by an app ("Me doing bak-bak…")
  only when the text is part of the moment, and held long enough to read.
- **Flatter the person.** If they'd wince at a frame, it's cut, however "dynamic" it is.

## 4. Where to cut
- **Cut on action:** hide the cut inside a movement (head turn, spin, hair flip, door).
  Keep the direction of motion consistent across the cut.
- **Cut on the look:** her eyes move, cut to what she sees, or to the next memory.
- **Cut after the expression completes** (romantic, sincere) or **right on its peak**
  (cute, funny, hype).
- **Match cut:** the same shape, pose, colour or motion across time (her smile at 5 → her
  smile now; a spin → a spin). Match cuts are the "how did they do that" moment of a personal film.
- **J-cut / L-cut:** a voice note starts before its picture (J), or a laugh carries over
  into the next shot (L). Sound leading picture feels intimate.
- **Jump cut:** time passing, comedy, or a stutter on purpose. Not as an accident.

## 5. Rhythm
- **The cut rate follows emotion and the song's section, and it varies.** Accelerate into a
  moment, then hold. Equal shot lengths read as mechanical; use long-short-short-long.
- **Song map:** verse = longer shots; pre-chorus = accelerate; chorus = on the beat;
  bridge / breakdown = slow, hold, breathe; final chorus = peak, then the big hold on the
  "us" shot.
- **Breathe after a peak:** hold at least 2 s after the emotional climax before anything moves on.
- **Meaning on the beat:** the biggest images on the biggest musical moments, and when
  there are lyrics, matching the line (a line about her smile on her smile).

| Shot | Romantic | Cute | Hype |
|---|---|---|---|
| Face with an expression | 2-5 s | 1-2 s | 0.4-0.8 s |
| Photo | 2-3 s (with a move) | 0.8-1.5 s (with a pop or doodle) | 0.25-0.5 s (photo-dump stutter) |
| Wide / place | 1.5-2.5 s | 1 s | 0.3-0.6 s |

## 6. Speed
- **Slow motion** (50-70%) for tender moments. Phone clips at 30 fps stutter below about 60%;
  keep slowed shots short, or interpolate (`speed_ramp.py --interp`).
- **Velocity / speed ramps:** fast → slow on the hit → fast. Build the ramped clip with
  `scripts/speed_ramp.py` (it prints where each point lands in output time), then place
  the slowest point on the beat.

## 7. Stills
- Prefer moving footage. When it's mostly photos, give the film **structure** (chapters,
  dates, a list), or it's a slideshow however it's cut.
- Every still gets a reason and a treatment that suits the mood: a push to the eyes, a
  polaroid drop, a doodle, a pairing with the clip from the same day.
- Don't show someone's own selfies back to them as filler. Pair each one with what it
  meant to the sender (a caption, a memory, an inside joke).

## 8. Sequencing
- **Arc, not shuffle:** a hook (the most "them" moment), then grouped by time, place or
  colour, escalating, ending on the "us" shot and the message.
- **Vary scale** (wide → medium → close) and keep **eye-trace** steady: on fast cuts, keep
  the face near the same spot on screen so the eye doesn't have to hunt.
- Separate similar shots. Two near-identical selfies back to back read as a mistake.

## 9. Effects budget
One signature device per film, used with intent. Each effect answers "what feeling does
this add?":
- glitch, RGB split, flash frames, whips, shake = energy, aggression, chaos;
- dissolves, leaks, bloom, slow motion = tenderness, memory;
- doodles, stickers, pops, freeze frames = play.
Energy devices never go in tender or sincere sections (`moods.md`).

## 10. Length
Personal films land at 30-90 s. A whole 3-minute song is long for a montage unless the
story develops across it. Offer the best 60-90 s of the song as a smooth edit
(`edit_song.py`), and always ask before cutting someone's song.

## 11. The recipient test (before rendering)
Watch the contact sheet and a draft as the person it's for:
- Do they smile in the first 3 seconds?
- Is there something only the sender would know or notice?
- Would they screenshot a frame, or reply with a voice note?
- Is every frame flattering?
- Does any effect look like a template?
If not, fix the shot log, not the effects.
