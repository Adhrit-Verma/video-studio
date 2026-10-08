# Camera language, and how to shoot each move in code

Camera is a choice the user makes in the brief. Each move below maps to kit pieces.
Pick 1-2 as the film's signature and use others sparingly: consistency reads as intent.

| Move | Feel | In code |
|---|---|---|
| **Locked / static** | graphic, confident, typographic | no transform; motion comes from the elements |
| **Slow push-in / pull-out** | attention, gravitas | `<Push from={1} to={1.06} beats={8}>`; or animate Stage `z` |
| **Drift** | calm, premium | Stage `ry`/`rx` changing a few degrees across the scene |
| **Settle to frontal** | "here it is": UI reveals | Stage starts tilted (rx 16-20, ry ±20-26, z -120..-200) and eases to ~0 with `rise(b,0,5)` |
| **Orbit** | objects, devices, 3D diagrams | Stage `ry` sweeping 20-40° across the scene; for photoreal products, the Blender orbit |
| **Crane / tilt** | reveal something below/above | Stage `rx` from 30 → 0 with `y` travel |
| **Fly-through / tunnel** | speed, abundance, a build before a drop | Layers at z = -i·gap + travel(b), accelerating; objects pass the camera |
| **Isometric / top-down** | diagrams, systems, maps | Stage rx 55-62, rz -35..-45, static or slow rz drift; labels counter-rotated |
| **Dolly across** | timelines, filmstrips, lists | slide a row of Layers in x past a fixed point (a scanner, a playhead) |
| **Whip pan** | energetic transition | `<WhipIn from="right">` at scene start (fast translate + motion blur) |
| **Zoom punch** | one big hit (a drop), never a pattern | a single quick scale 1→1.04→1 on that one hit; NOT `Film` punch across a section (reads as shake, see below) |
| **Dive into detail** | "look at this line" | scale a page with transform-origin on the detail; draw an outline around it |
| **Rack focus** | depth, storytelling | blur on the background leaf (`filter: blur(n)` on a Pic/leaf, not a 3D parent) swapping with the foreground |
| **Handheld** | documentary, UGC, honesty | `<Shake amount={4-8}>` around the scene |
| **Parallax layers** | depth in 2D styles | layers moving in x at different speeds (background slowest) |
| **Dutch angle** | tension, edgy styles | Stage `rz` 5-12° |
| **Match cut** | continuity between scenes | end scene A with a shape where scene B starts (same position/size) |
| **Letterbox** | cinematic | `<Letterbox ratio={2.39}>` |

## Rules of thumb
- Moves start on a beat (or a VO word) and settle; nothing drifts aimlessly.

## The camera is the viewer: keep it smooth, let the music move the elements
Learned on the Jimmy trailer (2026-10-05), from a user who rejected two versions:
- **Camera = smooth, always.** Pans, tilts, pushes, orbits and tracking are ONE continuous
  eased move per scene (`rise(b, 0, sceneLen, EASES.smooth)`), like a real dolly. The viewer
  rides the camera; anything jerky there feels like the viewer is being shaken.
- **Never tie the camera to the beat.** Two things were rejected as "useless shake":
  1. `Film` punch (scale bump) on every kick across whole sections;
  2. a stepped camera that jumps forward a notch on each kick ("hold, glide, hold").
  Also no `useHit()` pulses on big elements (wordmark, tiles): same jitter.
- **The beat drives the ELEMENTS and the TRANSITIONS only.** Entrances (words, cards,
  panels, badges, chart rows, tiles) snap to the nearest *measured* kick (`useSnap`) with a
  hard attack (snappy ease, ~0.4-0.55 beat). Cuts accelerate into the hit (ease-in zoom+blur
  over the last ~0.4 beat) and the next scene decelerates out of it (expo, ~0.45 beat). In
  quiet passages with no kicks, entrances keep the soft ease and cuts become dissolves.
- **Measure the hits on the final audio**, not a fixed grid: songs like slowed phonk put
  kicks on 3-3-2 eighths, so "every half beat" visibly misses. Weight them by strength.
- **Keep the layout inside the frame.** A tilted 3D grid with a moving camera pushed tiles
  out of frame; for a dense "everything else" grid use a flat, centred layout with a tiny
  smooth scale drift and let the tiles do the motion.

## The camera is the viewer: keep it smooth, let the music move the elements
Learned on the Jimmy trailer (2026-10-05), from a user who rejected two versions:
- **Camera = smooth, always.** Pans, tilts, pushes, orbits and tracking are ONE continuous
  eased move per scene (`rise(b, 0, sceneLen, EASES.smooth)`), like a real dolly. The viewer
  rides the camera; anything jerky there feels like the viewer is being shaken.
- **Never tie the camera to the beat.** Two things were rejected as "useless shake":
  1. `Film` punch (scale bump) on every kick across whole sections;
  2. a stepped camera that jumps forward a notch on each kick ("hold, glide, hold").
  Also no `useHit()` pulses on big elements (wordmark, tiles): same jitter.
- **The beat drives the ELEMENTS and the TRANSITIONS only.** Entrances (words, cards,
  panels, badges, chart rows, tiles) snap to the nearest *measured* kick (`useSnap`) with a
  hard attack (snappy ease, ~0.4-0.55 beat). Cuts accelerate into the hit (ease-in zoom+blur
  over the last ~0.4 beat) and the next scene decelerates out of it (expo, ~0.45 beat). In
  quiet passages with no kicks, entrances keep the soft ease and cuts become dissolves.
- **Measure the hits on the final audio**, not a fixed grid: songs like slowed phonk put
  kicks on 3-3-2 eighths, so "every half beat" visibly misses. Weight them by strength.
- **Keep the layout inside the frame.** A tilted 3D grid with a moving camera pushed tiles
  out of frame; for a dense "everything else" grid use a flat, centred layout with a tiny
  smooth scale drift and let the tiles do the motion.
- One camera move per scene. Content motion and camera motion should not fight.
- Faster styles: shorter moves (0.5-1 beat) and more cuts. Calm styles: 4-8 beat moves.
- 3D camera moves need depth to read: put layers at different z (40-200 px apart).
- On 9:16, big lateral moves feel faster (narrow frame): reduce x travel ~40%.
