# Social edit formats and trends

Snapshot: **October 2026.** Trends move fast: audio trends peak within 7-10 days and
format trends run 3-4 weeks before saturating (New Engen, Oct 2026). So:
- **check what's current** before leaning on a trend: search "Instagram Reels trends
  <month year>" (Later.com keeps a weekly list) and look at trending audio;
- **prefer references over lists:** ask the user, or the recipient's taste via the user, for
  1-3 reels they love, then extract the traits (pace, transitions, type, grade, overlays, sound);
- **craft first, trend second:** build on the mood and the editing (`moods.md`, `editing.md`)
  and add one trend accent. A trend can't rescue a film with no story.

Common platform advice for 2026: a strong hook in the first 2 s; cuts every 2-5 s for
general reels (faster for hype, slower for tender); cut to the music's structure.

## Evergreen formats and how to build them
| Format | What it is | Build it with |
|---|---|---|
| **Photo dump / cut-out collage** | 20-30 images flashing on the beat (0.2-0.4 s each), mixed scale, some cut-outs layered, ending on the best one held | shot log of stills; hard cuts on the grid; `StickerText` captions; final hold 2-3 s |
| **Scrapbook / stop-motion collage** | paper background, tape, cut-out photos, doodles, everything moving on threes; page flips | `Paper`, `TapeStrip`, `Polaroid`, `Doodle`, `useStepFrame(3)` |
| **Moving polaroid** | a clip playing inside a polaroid frame; a still that comes alive | `Polaroid` with an `OffthreadVideo` child; start on the photo, then the clip |
| **Velocity edit** | speed ramps synced to the beat: fast, slow on the hit, fast | `scripts/speed_ramp.py`, then place the slow point on the beat; motion-rich clips only |
| **Y2K digicam / camcorder** | orange date stamp, REC dot, harsh flash, contrasty saturated colour, slight softness | `Camcorder` overlay, `GRADES.digicam`, white flash pops on cuts |
| **Vlog timestamps** | time-of-day labels on each clip, no voiceover ("7:42 am · chai") | small mono label per shot, held 0.8 s+ |
| **Lyric edit** | one sung line at a time, handwritten or karaoke-highlighted, synced to the vocal | user supplies the lyrics; forced alignment (`examples/align.py`); traced glyphs |
| **Text-message / note storytelling** | a conversation or note appears line by line with typing dots | a generic chat or notes card (never copy an app's exact UI); `Stream` with key ticks |
| **Crumpled-paper message** | a wadded paper unfolds to reveal a handwritten line | paper texture + scale/rotate unfold + the sender's handwriting PNG |
| **"More to me" montage** | an opening statement, then quick photo montages of each interest | statement card → per-interest bursts → calm sign-off |
| **Rating / reaction** | a face reacts or rates; the comments argue | freeze frame + `StickerText` score |

## Regional notes (India)
- Hinglish captions in the couple's or friends' own words feel native; formal English can feel distant.
- Bollywood song edits and lyrical "status" videos are a familiar genre, so a plain lyric
  overlay reads as ordinary. A personal film needs the sender's own words or specific
  memories to stand out.
- WhatsApp Status trims long videos, so for status sharing keep a 30-60 s cut (check the
  current limit). DMs and chats can carry longer files.
