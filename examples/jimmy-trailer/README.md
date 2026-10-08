# Example: Jimmy launch trailer (60 s)

The film in the repo's README, built with the skill in one session from the
Jimmy codebase (an always-on assistant for Windows 11). All on-screen data is invented
("Northwind Fellowship"), exactly as in Jimmy's own README.

- `src/Video.jsx`: the 16 scenes (hook, tease, reveal, one shot per skill, grid, end card)
- `src/kit.jsx`, `src/theme.js`: the skill's kit and this film's keynote-dark theme
- `src/banner.jsx`: the repo's README art (`npx remotion still src/banner.jsx Banner out.png`)
- `video.json`: 97.998 BPM, 98 beats = 60 s

## Render it with your own song
The original track is not included (it isn't ours to share). Bring any song:

```bash
npm install
python ../../video-studio/scripts/edit_song.py public/song.mp3 --bpm 98 --map
python ../../video-studio/scripts/edit_song.py public/song.mp3 --bpm 98 --segments 30-41,12-20,44- --beats 98
npx remotion render src/index.js Film out/film.mp4 --props=out/props.json
python ../../video-studio/scripts/verify_sync.py out/film.mp4
```
Pick segments from the map so the drops land where `src/Video.jsx` expects them
(reveal at beat 25.5, second drop at 85.5, final chord at 92), or re-time the scenes.
