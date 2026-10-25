# The kit, CSS-3D, and the rules that silently break renders

## Why CSS-3D for UI and infographics
Real DOM in perspective: text stays vector-sharp at any angle, panels are real
components (their text can stream, numbers can count), and it renders fast. Use
`@remotion/three` (three.js) for particles, meshes and shaders; Blender for photoreal
products; CSS-3D for everything that is UI, type or diagram.

## The kit (src/kit.jsx) — everything visual reads src/theme.js
| Export | What |
|---|---|
| `Film` | root: timing context, kick pulse, format switch, camera punch, music, grain |
| `Scene from to` | a Sequence on the grid (beats, or seconds at bpm 60) |
| `useBeat()` | current beat within the scene |
| `rise(b, at, dur, ease?)` | 0→1 with the theme's motion feel; the workhorse |
| `EASES` | expo, snappy, bouncy, back, smooth, linear |
| `Reveal at dur out y blur scale` | enter / leave |
| `Words text at step accent` | word by word; accented words |
| `Stream text at step keys` | typewriter by words (streaming answers); `keys` adds a soft keypress per word |
| `Sfx at src volume` | a sound effect from `public/sfx/…`, `at` beats into the scene (sound.md §9) |
| `useEnergy()` | `{ energy, bass }` 0..1 at this frame from the master, for subtle audio-reactive glow/presence |
| `readSeconds(text)` / `useReadBeats(text)` | the reading-time floor in seconds / beats; `Words` warns when its `out` is too early |
| `Count to at dur format` | counting numbers |
| `Stage rx ry rz x y z persp` / `Layer x y z rx ry rz w h origin` | 3D camera and planes |
| `Push`, `Shake`, `WhipIn`, `Letterbox` | camera moves (see camera.md) |
| `Glow`, `Vignette`, `Flash`, `Cover`, `Grain` | light, framing, hits, 3D-safe fade, texture |
| `Center`, `Caption` | layout; both respect 9:16 safe areas |
| `Pic`, `ImageSeq` | images from public/, frame-locked image sequences |
| `head(size)`, `body(size)`, `ACCENT`, `accentFill`, `SURFACE`, `INK`, `MUTED`, `BG` | type and material from the theme |
| `useFormat()` / `useV()` | "wide" / "tall" / "square" / "portrait" |
| `Graded grade` / `GRADES` | mood colour grades for photos and clips: natural, warm, golden, pastel, faded, night, mono, digicam (a filter flattens 3D: never wrap a Stage) |
| `Doodle shape at dur size color width x y rot fill boil` / `DOODLES` | hand-drawn heart, circle, arrow, sparkle, star, underline, squiggle (or your own path) that draws itself, then boils |
| `StickerText at size color outline rot font` | chunky outlined sticker text that pops in |
| `Polaroid w ratio rot at caption` | a photo or clip (children) in a polaroid that drops in, with an optional handwritten caption |
| `Paper`, `TapeStrip w h x y rot` | scrapbook paper background and torn tape |
| `Camcorder date rec color font` | camcorder/digicam overlay: brackets, blinking REC, running time, orange date stamp |
| `useStepFrame(n)` | the current frame held for n frames (stop-motion "on twos/threes") |

Pattern for a 3D scene (style comes from the theme):
```jsx
const Demo = () => {
  const b = useBeat();
  const k = rise(b, 0, 5);                        // camera settles over 5 beats
  return (
    <>
      <Glow size={80} />
      <Stage rx={18 - 14 * k} ry={-22 + 18 * k} z={-160 + 120 * k}>
        <Layer w={1500} h={844}><Pic src="screen.png" width="100%" height="100%" dim={0.5} /></Layer>
        <Layer y={-320} z={160}><div style={{ ...SURFACE, padding: 20 }}>…</div></Layer>
      </Stage>
      <Caption><Reveal at={4}><span style={head(44)}>Plain line. <span style={ACCENT}>Payoff.</span></span></Reveal></Caption>
      <Cover at={0} dur={0.6} />
    </>
  );
};
```

## Rules (each broke a render once)
1. `opacity`, `filter`, `clip-path`, `mask` and `backdrop-filter` **flatten 3D**. On a
   Stage or a Layer with children the whole subtree goes flat. Put them on leaf
   elements only; to fade a 3D scene in, lay a `Cover` over it.
2. `clip-path` also clips the element's own `box-shadow`: for an outline that draws
   itself, use an unclipped glow element plus a clipped border element.
3. Counter-rotating a label to face the camera needs the inverse transforms in reverse
   order: stage `rotateX(58) rotateZ(-38)` → label `rotateZ(38deg) rotateX(-58deg)`
   (write it by hand; Layer applies X→Y→Z).
4. Cards that stand up from a tilted floor: `origin="50% 100%"`, `rx = -floorTilt * t`.
   Never override Layer's `style.transform` (it wipes the positioning).
5. Contrast: text over pages/images needs a chip (`SURFACE`) or a scrim.
6. Give every scene depth to move through: layers 40-200 px apart in z, and a camera
   move (see camera.md). Flat stacks with a moving camera look like cardboard.
7. Positions are px in the composition frame; restack per format with `useV()` /
   `useFormat()` instead of scaling.
8. Stills first: `contact_sheet.py` one beat per scene, a little after entrances start.
9. Remotion: `Html5Audio` takes `trimBefore` (frames); length comes from
   `calculateMetadata` so it follows the tempo; fonts via `@remotion/google-fonts/<Name>`.
