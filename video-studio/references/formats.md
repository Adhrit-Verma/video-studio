# Formats and platform safe zones

## Compositions in the template
| id | size | for | render |
|---|---|---|---|
| `Film` | 1920×1080 | YouTube, websites, pitches | `npm run render` |
| `FilmTall` | 1080×1920 | Reels, TikTok, Shorts, Stories | `npm run render:tall` |
| `FilmSquare` | 1080×1080 | feeds, LinkedIn | `npm run render:square` |
| `FilmPortrait` | 1080×1350 | Instagram feed | `npm run render:portrait` |
Add `-- --props=out/props.json` when there is music.

## Re-lay out; never crop
A center crop of 16:9 loses half of every side-by-side scene. Each scene branches on
`useFormat()` / `useV()`:

| Wide layout | Tall layout |
|---|---|
| items side by side (x ±500) | stacked (y offsets), same z |
| a 1500×844 screen plane | ~960×1500 (the image cover-crops) |
| headline + visual left/right | headline on top (~250-300 px from top), visual below |
| huge single word | smaller (must fit 1080 minus side padding) |
| wide timelines | narrower; stagger overlapping items in depth |
| lateral camera moves | ~40% less travel (a narrow frame exaggerates speed) |
| captions at the bottom | `Caption` lifts them above the app UI |

`Center` pads 130 px per side on tall formats so text wraps clear of the button rail.

## Safe zones (1080×1920; approximate, apps change)
| App | bottom (caption, name, audio) | right rail (like/comment/share) | top (header) |
|---|---|---|---|
| Instagram Reels | ~420 px | ~130 px, lower half | ~220 px |
| TikTok | ~480 px | ~140 px, lower half | ~160 px |
| YouTube Shorts | ~400 px | ~120 px, lower half | ~180 px |
Text and key UI stay out of these; visuals may bleed in. Check with
`contact_sheet.py --comp FilmTall --safe reels`.

## Posting notes for the user
- 30 fps, H.264 + AAC (Remotion default) suits every platform.
- Reels ≤ 90 s for reach; Shorts ≤ 3 min; TikTok up to 10 min (short wins).
- The first 1.5 s decides the scroll on social: the tall cut may need a stronger first
  frame than the wide one (start on the payoff).
- Cover frame: `finish.py` pulls the poster (the reveal, or the most legible fact) and
  bakes it in as frame 0, because Slack, X and Discord thumbnail frame 0. Upload the
  `.jpg` as the custom thumbnail where the platform allows it (Instagram, TikTok,
  YouTube, Facebook, LinkedIn); run it per format (the tall cut needs its own poster).
- Caption: `out/share-copy.txt`, written in the video's tone (tones.md).
- Muted autoplay: burn in captions where the story depends on words.
