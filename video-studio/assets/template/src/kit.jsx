// The animation kit: timing, type, reveals, CSS-3D stages, light, camera helpers and
// the format switch. Style-neutral: every colour, font and motion feel comes from theme.js.
import { createContext, useContext, useEffect, useRef } from "react";
import { AbsoluteFill, Easing, Html5Audio, Img, Sequence, continueRender, delayRender, interpolate, random, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme.js";

// --- time: scenes are timed in beats (with music) or seconds (bpm 60 = 1 beat per second)
export const FramesPerBeat = createContext(30);
export const Pulse = createContext(0);
export const Kicks = createContext({ beats: [], weights: [] });  // measured hits, in film beats
export const SceneFrom = createContext(0);
// Snap a scene-local beat onto the nearest real kick within `win` beats (quiet parts stay put).
export const useSnap = (win = 0.4) => {
  const { beats } = useContext(Kicks);
  const from = useContext(SceneFrom);
  return (at) => {
    let best = null;
    for (const k of beats) { const d = Math.abs(k - from - at); if (d <= win && (best == null || d < Math.abs(best - at))) best = k - from; }
    return best ?? at;
  };
};
// 0..1 hit envelope for this frame (sharp attack, fast decay), weighted by kick strength.
export const useHit = () => useContext(Pulse);
export const Energy = createContext({ energy: 0, bass: 0 });  // 0..1 music loudness / bass at this frame
export const useEnergy = () => useContext(Energy);
export const Format = createContext("wide");      // "wide" 16:9 | "tall" 9:16 | "square" 1:1 | "portrait" 4:5
export const useFormat = () => useContext(Format);
export const useV = () => useContext(Format) === "tall";
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" };

// Motion feel: the style's easing. The attack is always at the start of the curve.
export const EASES = {
  expo: Easing.bezier(0.16, 1, 0.3, 1),          // fast start, long settle: premium, calm
  snappy: Easing.bezier(0.2, 0.9, 0.1, 1),       // quick and crisp: tech, UI-heavy
  bouncy: Easing.bezier(0.34, 1.56, 0.64, 1),    // overshoots: playful, friendly
  back: Easing.bezier(0.68, -0.4, 0.27, 1.4),    // anticipates and overshoots: cartoon, kinetic
  smooth: Easing.bezier(0.45, 0, 0.55, 1),       // ease-in-out: documentary, cinematic
  linear: Easing.linear,                         // mechanical, retro, data
};
const EASE = EASES[theme.motion] ?? EASES.expo;
export const useBeat = () => useCurrentFrame() / useContext(FramesPerBeat);
export const rise = (b, at, dur = 1, ease = EASE) => interpolate(b, [at, at + dur], [0, 1], { ...clamp, easing: ease });

// Reading time (references/techniques.md → Readability): a label ~0.8 s, a line 0.3 s per
// word and at least 1.2 s, counted once the whole line is on screen and settled.
export const readSeconds = (text) => {
  const n = String(text).trim().split(/\s+/).filter(Boolean).length;
  return n <= 3 ? 0.8 : Math.max(1.2, 0.3 * n);
};
export const useReadBeats = (text) => (readSeconds(text) * useVideoConfig().fps) / useContext(FramesPerBeat);

export const pulseAt = (t, kicks, weights, decay = 0.13) => {
  let i = -1;
  while (i + 1 < kicks.length && kicks[i + 1] <= t) i++;
  return i < 0 ? 0 : (weights[i] ?? 1) * Math.exp(-(t - kicks[i]) / decay);
};

// --- look, from the theme ---------------------------------------------------
export const { font: fontFamily, ink: INK, muted: MUTED, bg: BG } = theme;
export const ACCENT = theme.accent.length > 1
  ? { backgroundImage: `linear-gradient(95deg, ${theme.accent.join(", ")})`, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent" }
  : { color: theme.accent[0] };
export const accentFill = theme.accent.length > 1 ? `linear-gradient(135deg, ${theme.accent.join(", ")})` : theme.accent[0];
export const SURFACE = {
  background: theme.surface.background, borderRadius: theme.surface.radius, fontFamily, color: INK,
  boxShadow: `0 0 0 1px ${theme.surface.border}, ${theme.surface.shadow}`,
  ...(theme.surface.blur ? { backdropFilter: `blur(${theme.surface.blur}px)` } : {}),
};
export const head = (size, extra) => ({
  fontFamily, fontWeight: theme.headline.weight, fontSize: size, letterSpacing: theme.headline.tracking,
  lineHeight: theme.headline.lineHeight, textTransform: theme.headline.transform, color: INK, ...extra,
});
export const body = (size, extra) => ({ fontFamily, fontWeight: 500, fontSize: size, lineHeight: 1.4, color: MUTED, ...extra });

// --- layout -----------------------------------------------------------------
// On 9:16 the side padding keeps text clear of the apps' right-hand button rail.
export const Center = ({ children, style }) => (
  <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", textAlign: "center",
    padding: useV() ? "0 130px" : 0, ...style }}>{children}</AbsoluteFill>
);

// A caption strip: the frame bottom on 16:9, above the Reels/TikTok/Shorts UI on 9:16.
export const Caption = ({ children, bottom = 50 }) => (
  <div style={{ position: "absolute", bottom: useV() ? 470 : bottom, width: "100%", textAlign: "center",
    padding: useV() ? "0 90px" : 0 }}>{children}</div>
);

// A scene placed on the grid: <Scene from={16} to={24}>...</Scene> (beats).
const easeIn = Easing.bezier(0.7, 0, 0.84, 0);
const SceneBody = ({ len, enter, exit, children, bg }) => {
  const b = useBeat();
  const i = enter ? 1 - rise(b, 0, enter === "hard" ? 0.45 : 0.9, EASES.expo) : 0;
  const o = exit ? interpolate(b, [len - (exit === "hard" ? 0.4 : 0.7), len], [0, 1], { ...clamp, easing: easeIn }) : 0;
  const zoom = enter === "hard" ? 0.1 : 0.04;
  return (
    <AbsoluteFill style={{ background: bg, transform: `scale(${1 + zoom * i + 0.09 * o})`,
      filter: i + o > 0.001 ? `blur(${i * (enter === "hard" ? 20 : 10) + o * 16}px)` : undefined,
      opacity: 1 - (enter === "soft" ? i : 0) - (exit === "soft" ? o : 0) }}>{children}</AbsoluteFill>
  );
};
export const Scene = ({ from, to, children, bg = BG, enter, exit }) => {
  const B = useContext(FramesPerBeat);
  return (
    <Sequence from={Math.round(from * B)} durationInFrames={Math.round((to - from) * B)}>
      <SceneFrom.Provider value={from}><SceneBody len={to - from} enter={enter} exit={exit} bg={bg}>{children}</SceneBody></SceneFrom.Provider>
    </Sequence>
  );
};

// --- motion -----------------------------------------------------------------
// Enter (fade + rise + blur + scale, as the style wants), optionally leave. `at`/`out` in beats.
export const Reveal = ({ at = 0, dur = 1.2, out, outDur = 0.5, y = 28, blur = 18, scale = 1, inline, children, style, snap = true }) => {
  const b = useBeat();
  const s = useSnap();
  const t0 = snap ? s(at) : at;
  const hit = t0 !== at;
  const p = rise(b, t0, hit ? Math.min(dur, 0.55) : dur, hit ? EASES.snappy : EASE);
  const o = out == null ? 0 : rise(b, snap ? s(out) : out, outDur);
  return (
    <div style={{ display: inline ? "inline-block" : "block", opacity: p * (1 - o),
      transform: `translateY(${(1 - p) * (hit ? y * 1.6 : y) - o * 12}px) scale(${(hit ? 0.92 : scale) + (1 - (hit ? 0.92 : scale)) * p})`,
      filter: blur ? `blur(${(1 - p) * blur + o * blur}px)` : undefined, ...style }}>{children}</div>
  );
};

// Word by word, `step` beats apart. Indices in `accent` get the accent colour/gradient.
// With `out`, warns in the render log when the line leaves before it can be read.
const warned = new Set();
export const Words = ({ text, at = 0, step = 0.5, accent = [], out, style, y = 18, blur = 12, scale = 1 }) => {
  const words = text.split(" ");
  const need = useReadBeats(text);
  const held = out == null ? Infinity : out - (at + (words.length - 1) * step + 0.9);
  if (held < need && !warned.has(text)) {
    warned.add(text);
    console.warn(`[readability] "${text}" holds ${held.toFixed(1)} beats; it needs ${need.toFixed(1)}. Move \`out\` later or cut words.`);
  }
  return (
    <div style={style}>
      {words.map((w, i) => (
        <Reveal key={i} inline at={at + i * step} dur={0.9} out={out} y={y} blur={blur} scale={scale} style={{ marginRight: "0.24em" }}>
          <span style={accent.includes(i) ? ACCENT : undefined}>{w}</span>
        </Reveal>
      ))}
    </div>
  );
};

// A sound effect from public/ (copied from <skill>/assets/sfx/), starting `at` beats into
// the scene. Mixing: references/sound.md → "Sound effects" (they sit under the music).
export const Sfx = ({ at = 0, src, volume = 0.4 }) => {
  const B = useContext(FramesPerBeat);
  return (
    <Sequence from={Math.round(at * B)} layout="none">
      <Html5Audio src={staticFile(src)} volume={volume} />
    </Sequence>
  );
};

// Typewriter by words (answers "streaming in"), with a caret while typing.
// `keys` adds a soft keypress per word (public/sfx/keyboard/keypress-001..032.wav);
// pass a number for its volume.
export const Stream = ({ text, at, step, caret = true, keys }) => {
  const b = useBeat();
  const words = text.split(" ");
  const n = Math.max(0, Math.min(words.length, Math.floor((b - at) / step) + 1));
  return (
    <span>
      {words.slice(0, n).join(" ")}{caret && n > 0 && n < words.length && <span style={{ opacity: 0.5 }}> ▍</span>}
      {keys && words.map((w, i) => (
        <Sfx key={i} at={at + i * step} volume={typeof keys === "number" ? keys : 0.18}
          src={`sfx/keyboard/keypress-${String(1 + Math.floor(random(`${text}${i}`) * 32)).padStart(3, "0")}.wav`} />
      ))}
    </span>
  );
};

// A number counting up: <Count to={1200} at={1} dur={2} format={(n) => `${n}+`} />
export const Count = ({ to, from = 0, at = 0, dur = 2, format = (n) => n.toLocaleString(), style }) => {
  const b = useBeat();
  return <span style={style}>{format(Math.round(from + (to - from) * rise(b, at, dur)))}</span>;
};

export const Flash = ({ at, dur = 0.6, color = "#fff", peak = 1 }) => {
  const b = useBeat();
  return <AbsoluteFill style={{ background: color, pointerEvents: "none",
    opacity: interpolate(b, [at, at + 0.05, at + dur], [0, peak, 0], clamp) }} />;
};

// Soft coloured light behind the subject; breathes with the kicks and the music's energy.
export const Glow = ({ color = `${theme.accent[0]}44`, at = 0, size = 60, x = 50, y = 55 }) => {
  const b = useBeat();
  const pulse = useContext(Pulse);
  const { energy } = useEnergy();
  return <AbsoluteFill style={{ opacity: rise(b, at, 1) * (0.75 + 0.35 * pulse + 0.2 * energy),
    background: `radial-gradient(ellipse ${size}% ${size * 0.8}% at ${x}% ${y}%, ${color}, transparent 70%)` }} />;
};

export const Vignette = ({ strength = 0.8, color = "0,0,0" }) => (
  <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 50%, rgba(${color},0), rgba(${color},${strength}) 75%)` }} />
);

// A fade-in that doesn't flatten the 3D underneath: a sheet of the stage colour that lifts.
export const Cover = ({ at = 0, dur = 1, color = BG }) => {
  const b = useBeat();
  return <AbsoluteFill style={{ background: color, opacity: 1 - rise(b, at, dur) }} />;
};

// --- camera -----------------------------------------------------------------
// Slow push / pull on a whole scene.
export const Push = ({ from = 1, to = 1.06, beats = 8, children }) => {
  const b = useBeat();
  return <AbsoluteFill style={{ transform: `scale(${interpolate(b, [0, beats], [from, to], clamp)})` }}>{children}</AbsoluteFill>;
};

// Handheld: a small, smooth, deterministic wobble (documentary, UGC styles).
export const Shake = ({ amount = 6, children }) => {
  const f = useCurrentFrame();
  const n = (seed) => Math.sin(f * 0.11 + random(seed) * 6) * 0.6 + Math.sin(f * 0.037 + random(`${seed}2`) * 6) * 0.4;
  return <AbsoluteFill style={{ transform: `translate(${n("x") * amount}px, ${n("y") * amount}px) rotate(${n("r") * amount * 0.05}deg)` }}>{children}</AbsoluteFill>;
};

// Whip pan: the scene arrives fast with motion blur from one side (use at a scene start).
export const WhipIn = ({ from = "right", dur = 0.5, children }) => {
  const b = useBeat();
  const p = rise(b, 0, dur, EASES.snappy);
  const d = { right: [1, 0], left: [-1, 0], up: [0, -1], down: [0, 1] }[from];
  return <AbsoluteFill style={{ transform: `translate(${d[0] * (1 - p) * 110}%, ${d[1] * (1 - p) * 110}%)`,
    filter: p < 1 ? `blur(${(1 - p) * 30}px)` : undefined }}>{children}</AbsoluteFill>;
};

// Cinematic bars (2.39:1 inside 16:9), sliding in.
export const Letterbox = ({ at = 0, ratio = 2.39 }) => {
  const b = useBeat();
  const bar = `${((1 - 16 / 9 / ratio) / 2) * 100 * rise(b, at, 1)}%`;
  return <><div style={{ position: "absolute", top: 0, left: 0, right: 0, height: bar, background: "#000" }} />
    <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: bar, background: "#000" }} /></>;
};

// Film grain for cinematic / retro looks (theme.grain sets the default strength).
export const Grain = ({ amount = theme.grain }) => {
  const f = useCurrentFrame();
  if (!amount) return null;
  return (
    <AbsoluteFill style={{ opacity: amount, mixBlendMode: "overlay", pointerEvents: "none" }}>
      <svg width="100%" height="100%"><filter id="grain"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 60} /></filter>
        <rect width="100%" height="100%" filter="url(#grain)" /></svg>
    </AbsoluteFill>
  );
};

// --- 3D: CSS perspective keeps UI razor sharp at any angle ---------------------
// opacity / filter / clip-path / backdrop-filter on an element flatten its 3D children:
// put them only on leaf elements, never on a Stage or on a Layer that has children.
export const Stage = ({ rx = 0, ry = 0, rz = 0, x = 0, y = 0, z = 0, persp = 1600, children }) => (
  <AbsoluteFill style={{ perspective: persp, perspectiveOrigin: "50% 45%" }}>
    <AbsoluteFill style={{ transformStyle: "preserve-3d",
      transform: `translate3d(${x}px, ${y}px, ${z}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg)` }}>
      {children}
    </AbsoluteFill>
  </AbsoluteFill>
);

// Positioned from its parent's centre; z > 0 is toward the camera.
export const Layer = ({ x = 0, y = 0, z = 0, rx = 0, ry = 0, rz = 0, w, h, origin, children, style }) => (
  <div style={{ position: "absolute", left: "50%", top: "50%", width: w, height: h, transformStyle: "preserve-3d",
    transformOrigin: origin,
    transform: `translate(-50%, -50%) translate3d(${x}px, ${y}px, ${z}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${rz}deg)`,
    ...style }}>{children}</div>
);

// An image from public/ (screenshot, mock page, render).
export const Pic = ({ src, width, height, dim = 1, radius = theme.surface.radius, style }) => (
  <Img src={staticFile(src)} style={{ width, height, objectFit: "cover", borderRadius: radius, display: "block",
    filter: dim === 1 ? undefined : `brightness(${dim})`, boxShadow: theme.surface.shadow, ...style }} />
);

// A rendered image sequence (Blender etc.): public/<dir>/0001.jpg ..., frame-locked to the scene.
export const ImageSeq = ({ dir, count, speed = 1, ext = "jpg", style }) => {
  const f = useCurrentFrame();
  const n = String(Math.min(count, Math.floor(f * speed) + 1)).padStart(4, "0");
  return <Img src={staticFile(`${dir}/${n}.${ext}`)}
    style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", ...style }} />;
};

// --- handmade, cute and memory looks (references/moods.md, references/trends.md) -------------
// Stop-motion time: hold each pose for n frames ("on twos/threes"), for a handmade, scrapbook feel.
// Use it in place of useCurrentFrame: const f = useStepFrame(3).
export const useStepFrame = (n = 2) => { const f = useCurrentFrame(); return f - (f % n); };

// Colour grades by mood: a filter for the media plus a tint over it. Wrap photos and clips only:
// a filter flattens 3D children (css-3d.md rule 1), so never wrap a Stage.
export const GRADES = {
  natural: { filter: "contrast(1.03) saturate(1.04)" },
  warm: { filter: "contrast(1.05) saturate(1.08) sepia(0.12)", tint: "rgba(255,170,110,0.10)", blend: "soft-light" },
  golden: { filter: "contrast(1.08) saturate(1.15) sepia(0.22) brightness(1.03)", tint: "rgba(255,185,90,0.14)", blend: "soft-light" },
  pastel: { filter: "contrast(0.9) saturate(0.85) brightness(1.08)", tint: "rgba(255,205,230,0.14)", blend: "screen" },
  faded: { filter: "contrast(0.86) saturate(0.78) sepia(0.15) brightness(1.06)", tint: "rgba(70,90,110,0.12)", blend: "lighten" },
  night: { filter: "contrast(1.1) saturate(0.9) brightness(0.95)", tint: "rgba(40,80,170,0.12)", blend: "soft-light" },
  mono: { filter: "grayscale(1) contrast(1.15) brightness(1.02)" },
  digicam: { filter: "contrast(1.18) saturate(1.3) brightness(1.06) blur(0.4px)", tint: "rgba(0,255,210,0.04)", blend: "screen" },
};
export const Graded = ({ grade = "natural", children, style }) => {
  const g = GRADES[grade] ?? GRADES.natural;
  return (
    <AbsoluteFill style={style}>
      <AbsoluteFill style={{ filter: g.filter }}>{children}</AbsoluteFill>
      {g.tint && <AbsoluteFill style={{ background: g.tint, mixBlendMode: g.blend, pointerEvents: "none" }} />}
    </AbsoluteFill>
  );
};

// Hand-drawn doodles that draw themselves, then "boil" (a tiny wobble every 4 frames, like
// redrawn animation). `shape` is a name below or your own SVG path in a 0..100 box.
// Positioned from the parent's centre like Layer: x, y in px. `at`/`dur` in beats.
export const DOODLES = {
  heart: "M50 84 C22 64 8 46 14 31 C20 16 40 15 50 33 C60 15 80 16 86 31 C92 46 79 63 47 86",
  circle: "M70 16 C40 4 9 22 11 52 C13 82 50 95 77 81 C97 69 95 33 73 19 C61 11 45 11 34 16",
  arrow: "M12 78 C30 66 56 48 84 22 M66 19 L85 20 L81 39",
  sparkle: "M50 8 C53 37 62 47 92 50 C62 53 53 63 50 92 C47 63 38 53 8 50 C38 47 47 37 50 8 Z",
  star: "M50 8 L61 38 L93 39 L67 58 L77 89 L50 70 L23 89 L33 58 L7 39 L39 38 Z",
  underline: "M6 62 C30 52 62 58 94 47",
  squiggle: "M4 50 C14 28 24 72 34 50 C44 28 54 72 64 50 C74 28 84 72 96 50",
};
export const Doodle = ({ shape = "heart", at = 0, dur = 0.6, size = 160, color = "#fff", width = 5, x = 0, y = 0, rot = 0, fill, boil = true, style }) => {
  const b = useBeat();
  const f = useStepFrame(4);
  const p = rise(b, at, dur, Easing.inOut(Easing.quad));
  if (p <= 0) return null;
  const j = (k) => (boil ? (random(`${shape}${k}${f}`) - 0.5) : 0);
  return (
    <svg width={size} height={size} viewBox="0 0 100 100"
      style={{ position: "absolute", left: "50%", top: "50%", overflow: "visible",
        transform: `translate(${x - size / 2 + j("x") * 2}px, ${y - size / 2 + j("y") * 2}px) rotate(${rot + j("r") * 3}deg)`, ...style }}>
      <path d={DOODLES[shape] ?? shape} fill={fill ?? "none"} fillOpacity={fill ? rise(b, at + dur * 0.8, 0.3) : 0}
        stroke={color} strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" vectorEffect="non-scaling-stroke"
        pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

// Sticker text: chunky, outlined, slightly tilted, pops in with an overshoot.
export const StickerText = ({ children, at = 0, size = 64, color = "#ff4f8b", outline = "#fff", rot = -4, font = fontFamily, style }) => {
  const p = rise(useBeat(), at, 0.5, EASES.back);
  const o = Math.max(2, size * 0.09);
  const ring = Array.from({ length: 12 }, (_, i) => {
    const a = (i / 12) * Math.PI * 2;
    return `${(Math.cos(a) * o).toFixed(1)}px ${(Math.sin(a) * o).toFixed(1)}px 0 ${outline}`;
  }).join(", ");
  return (
    <div style={{ display: "inline-block", fontFamily: font, fontWeight: 800, fontSize: size, lineHeight: 1.05, color,
      textShadow: `${ring}, 0 ${o * 1.6}px ${o * 2}px rgba(0,0,0,0.35)`, opacity: Math.min(1, p * 3),
      transform: `rotate(${rot}deg) scale(${p})`, ...style }}>{children}</div>
  );
};

// A polaroid: photo or clip inside (children), optional handwritten caption, drops in at `at`.
export const Polaroid = ({ w = 420, ratio = 1, rot = -3, at = 0, caption, captionFont = fontFamily, captionColor = "#333", children, style }) => {
  const p = rise(useBeat(), at, 0.8, EASES.back);
  const pad = w * 0.06, img = w - pad * 2;
  return (
    <div style={{ position: "relative", width: w, padding: `${pad}px ${pad}px ${pad * 3.6}px`, background: "#f7f3ea",
      boxShadow: "0 24px 50px rgba(0,0,0,0.45), 0 3px 8px rgba(0,0,0,0.25)", opacity: Math.min(1, p * 3),
      transform: `translateY(${(1 - p) * -80}px) rotate(${rot + (1 - p) * 8}deg) scale(${1.2 - 0.2 * p})`, ...style }}>
      <div style={{ position: "relative", width: img, height: img / ratio, overflow: "hidden", background: "#222" }}>{children}</div>
      {caption && <div style={{ position: "absolute", left: 0, right: 0, bottom: pad * 0.9, textAlign: "center", fontFamily: captionFont,
        fontSize: w * 0.075, color: captionColor }}>{caption}</div>}
    </div>
  );
};

// Paper background (fibres + a soft edge burn) for scrapbook and handmade films.
export const Paper = ({ color = "#f3ead8", grain = 0.5 }) => (
  <AbsoluteFill style={{ background: color }}>
    <svg width="100%" height="100%" style={{ position: "absolute", inset: 0, opacity: grain, mixBlendMode: "multiply" }}>
      <filter id="paper-fibres"><feTurbulence type="fractalNoise" baseFrequency="0.035 0.9" numOctaves="3" seed="7" />
        <feColorMatrix values="0 0 0 0 0.55  0 0 0 0 0.5  0 0 0 0 0.42  0 0 0 0.35 0" /></filter>
      <rect width="100%" height="100%" filter="url(#paper-fibres)" />
    </svg>
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(80,50,20,0.18))" }} />
  </AbsoluteFill>
);

// A strip of tape with torn ends; x, y from the parent's centre.
const torn = (() => {
  const l = [], r = [];
  for (let i = 0; i <= 8; i++) { l.push(`${i % 2 ? 4 : 0}% ${i * 12.5}%`); r.unshift(`${i % 2 ? 96 : 100}% ${i * 12.5}%`); }
  return `polygon(${[...l, ...r].join(", ")})`;
})();
export const TapeStrip = ({ w = 160, h = 44, x = 0, y = 0, rot = -8, color = "rgba(255,240,180,0.72)" }) => (
  <div style={{ position: "absolute", left: "50%", top: "50%", width: w, height: h, clipPath: torn,
    background: `linear-gradient(180deg, rgba(255,255,255,0.25), transparent 40%), ${color}`,
    transform: `translate(${x - w / 2}px, ${y - h / 2}px) rotate(${rot}deg)` }} />
);

// Camcorder / digicam overlay: corner brackets, blinking REC, running time, orange date stamp.
export const Camcorder = ({ date = "OCT 25 2026", rec = true, color = "#ffb030", font = "'Courier New', monospace" }) => {
  const f = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const s = Math.min(width, height) / 1080, m = 50 * s, L = 70 * s, t = Math.max(2, 4 * s);
  const sec = Math.floor(f / fps);
  const tc = [Math.floor(sec / 3600), Math.floor(sec / 60) % 60, sec % 60].map((n) => String(n).padStart(2, "0")).join(":");
  const label = { position: "absolute", fontFamily: font, fontWeight: 700, fontSize: 42 * s, color: "#fff", letterSpacing: "0.08em", textShadow: "0 0 4px rgba(0,0,0,0.6)" };
  const corner = (pos) => <div style={{ position: "absolute", width: L, height: L, borderColor: "rgba(255,255,255,0.85)", borderStyle: "solid", borderWidth: 0, ...pos }} />;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {corner({ left: m, top: m, borderLeftWidth: t, borderTopWidth: t })}
      {corner({ right: m, top: m, borderRightWidth: t, borderTopWidth: t })}
      {corner({ left: m, bottom: m, borderLeftWidth: t, borderBottomWidth: t })}
      {corner({ right: m, bottom: m, borderRightWidth: t, borderBottomWidth: t })}
      {rec && <div style={{ ...label, left: m + L * 0.4, top: m + L * 0.45 }}>
        <span style={{ color: "#ff3b30", opacity: f % fps < fps * 0.6 ? 1 : 0 }}>●</span> REC</div>}
      <div style={{ ...label, right: m + L * 0.4, top: m + L * 0.45 }}>▮▮▮▯</div>
      <div style={{ ...label, left: m + L * 0.4, bottom: m + L * 0.45 }}>▶ {tc}</div>
      <div style={{ ...label, right: m + L * 0.4, bottom: m + L * 0.45, color, textShadow: `0 0 8px ${color}99` }}>{date}</div>
    </AbsoluteFill>
  );
};

// --- layout check: warns in the render/stills log, so layout bugs can't slip past --------
// For visible text >= 18px: "[layout] frame N: \"…\" runs off the frame (right 34px)".
// For headlines >= 40px: "[layout] frame N: \"…\" leaves \"you?\" alone on its last line".
const layoutSeen = new Set();
const visibleOpacity = (el) => {
  let o = 1;
  for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= parseFloat(getComputedStyle(e).opacity || "1");
  return o;
};
export const LayoutCheck = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const ref = useRef(null);
  useEffect(() => {
    // measure on the next animation frame, once the frame is really laid out (before that the
    // page is parked off-screen at zero size); hold the screenshot until it's done
    const handle = delayRender("layout check");
    const id = requestAnimationFrame(() => { try { check(); } finally { continueRender(handle); } });
    return () => { cancelAnimationFrame(id); continueRender(handle); };
  });
  const check = () => {
    const root = ref.current?.parentElement;              // the film's frame
    if (!root) return;
    const box = root.getBoundingClientRect();
    if (box.width < 2) return;
    const k = box.width / width || 1;
    const warn = (key, msg) => { if (!layoutSeen.has(key)) { layoutSeen.add(key); console.warn(`[layout] frame ${frame}: ${msg}`); } };
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const blocks = new Map();
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const text = n.textContent.trim();
      const el = n.parentElement;
      if (!text || !el) continue;
      const size = parseFloat(getComputedStyle(el).fontSize);
      if (size < 18 || visibleOpacity(el) < 0.5 || getComputedStyle(el).visibility === "hidden") continue;
      const range = document.createRange();
      range.selectNodeContents(n);
      for (const rc of range.getClientRects()) {
        const l = (rc.left - box.left) / k, t = (rc.top - box.top) / k;
        const off = Math.max(-l, l + rc.width / k - width, -t, t + rc.height / k - height);
        if (off > 2 && rc.width > 0) warn(`off:${text}`, `"${text.slice(0, 40)}" runs off the frame (${Math.round(off)}px)`);
      }
      if (size >= 40) {                                   // group headline words by their block parent
        let b = el;
        while (b && getComputedStyle(b).display.startsWith("inline")) b = b.parentElement;
        if (!blocks.has(b)) blocks.set(b, []);
        const rc = range.getBoundingClientRect();
        blocks.get(b).push({ text, top: rc.top, h: rc.height });
      }
    }
    for (const words of blocks.values()) {
      const lines = [];
      for (const w of words) {
        const line = lines.find((l) => Math.abs(l.top - w.top) < w.h * 0.5);
        line ? line.words.push(w.text) : lines.push({ top: w.top, words: [w.text] });
      }
      if (lines.length < 2) continue;
      lines.sort((a, z) => a.top - z.top);
      const last = lines[lines.length - 1].words.join(" ").trim();
      if (!last.includes(" ")) {
        const all = lines.map((l) => l.words.join(" ")).join(" / ");
        warn(`orphan:${all}`, `"${all.slice(0, 60)}" leaves "${last}" alone on its last line`);
      }
    }
  };
  return <span ref={ref} style={{ display: "none" }} />;
};

// --- the film: contexts, the kick punch, the music ----------------------------
// punch: [[fromBeat, toBeat], ...] where the camera may punch on kicks.
// energy / bass: per-frame 0..1 envelopes of the master (master_audio.py), for useEnergy().
export const Film = ({ fps, bpm, music, offset = 0, kicks = [], kickWeights = [], energy = [], bass = [], format = "wide",
  punch = [], punchAmount = 0.03, totalBeats, children }) => {
  const B = (fps * 60) / bpm;
  const frame = useCurrentFrame();
  const beat = frame / B;
  const pulse = pulseAt(frame / fps, kicks, kickWeights, 0.11);
  const punching = punch.some(([a, z]) => beat >= a && beat < z);
  const total = Math.round(totalBeats * B);
  return (
    <FramesPerBeat.Provider value={B}>
      <Kicks.Provider value={{ beats: kicks.map((t) => (t * bpm) / 60), weights: kickWeights }}>
      <Pulse.Provider value={pulse}>
        <Energy.Provider value={{ energy: energy[frame] ?? 0, bass: bass[frame] ?? 0 }}>
          <Format.Provider value={format}>
            <AbsoluteFill style={{ background: BG, transform: `scale(${1 + (punching ? punchAmount * pulse : 0)})` }}>
              {children}
              <Grain />
              <LayoutCheck />
              {music && <Html5Audio src={staticFile(music)} trimBefore={Math.round(offset * fps)}
                volume={(f) => interpolate(f, [total - 12, total], [1, 0], clamp)} />}
            </AbsoluteFill>
          </Format.Provider>
        </Energy.Provider>
      </Pulse.Provider>
      </Kicks.Provider>
    </FramesPerBeat.Provider>
  );
};
