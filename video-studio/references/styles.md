# Style menu

Each family is a starting point: translate it into `src/theme.js` (tokens) plus a few
scene-level habits. Mix families when the user asks (e.g. "clean light + isometric
diagrams"). When the product has a strong brand, its own colours and font win over the
family's defaults. Brand names below describe a *feel*; never copy another company's
logo, UI or trade dress.

| Family | Feels like | theme.js | Habits |
|---|---|---|---|
| **Keynote dark** | premium hardware/software reveal | bg near-black, ink #f5f5f7, 1-2 cool accent gradient, dark glass surface, 700-800 tight type, motion `expo` | huge short headlines, glows, UI floating in depth, a flat wordmark slam on the drop, lots of black space |
| **Clean light** | calm SaaS, docs, productivity | bg #f7f7f5/#fff, ink #111, muted #666, one brand accent, white cards with soft shadow, radius 16-24, motion `snappy` | real UI large and legible, subtle 3D tilt, cursor-driven demos, captions under UI |
| **Bold kinetic type** | ads, hype, social | bg solid brand colour or black, ink white, accent loud, headline 800-900 `uppercase`, tight tracking, motion `back`/`snappy` | words ARE the visuals: scale slams, masks, split-flap, text filling the frame, cuts every beat |
| **Playful / rounded** | consumer apps, kids, friendly tools | pastel bg, saturated accents, radius 32+, rounded font (Nunito, Baloo, Fredoka), motion `bouncy` | squash-and-stretch entrances, stickers/emoji-like shapes, bouncing cards, confetti on wins |
| **Glassmorphism** | modern OS, fintech, AI | gradient/blurred colour field bg, frosted surfaces (`surface.blur` 20-40, 2D scenes only), white ink | blobs drifting behind glass, parallax, soft light sweeps |
| **Editorial / serif** | writing, research, luxury, culture | off-white or deep ink bg, serif display (Fraunces, Playfair, Instrument Serif), generous leading, motion `smooth` | slow reveals, pull quotes, big numerals, thin rules, image crops like a magazine |
| **Retro / VHS** | nostalgia, games, indie | warm faded palette, grain 0.12+, scanlines, chunky pixel or 80s fonts, motion `linear` | glitches, RGB split on hits, tape-stop transitions, CRT curvature |
| **Neon / cyber** | dev tools, security, gaming, AI | bg #05050a, neon cyan/magenta, mono font (JetBrains Mono, Space Mono), motion `snappy` | terminal typing, grid floors, wireframe 3D, glow trails, data rain |
| **Cinematic / documentary** | brand films, stories, founders | natural palette, letterbox 2.39, grain 0.06, serif or refined sans, motion `smooth` | slow pushes, handheld, rack-focus blur, title cards, silence and room tone |
| **Isometric / illustrative** | explainers, infrastructure, workflows | light or dark bg, flat shapes, 3-4 colours, rx 55-60 / rz -45 stages | diagrams that build piece by piece, flows of dots, labels counter-rotated to face camera |
| **Brutalist** | design tools, fashion, art | high contrast, raw grid, huge type, hard edges radius 0, motion `linear` | hard cuts, no easing, overlapping text blocks, visible grid lines |
| **Product's own system** | anything with a strong brand | tokens from discovery (colours, font, radius, surface) | the video looks like the product: its real components, its tone of voice |

## Turning a choice into tokens
- **Palette:** 1 background, 1 ink, 1 muted, 1-3 accents. Check contrast of captions on
  every background they cross (white text on a white page vanishes).
- **Type:** 1 display family (+ optionally 1 text family). `@remotion/google-fonts/<Name>`
  for Google fonts; the product's own font file via `@remotion/fonts`.
- **Surface:** how UI panels are made (glass, paper, flat, outlined, neumorphic).
- **Motion preset** (`theme.motion`): matches the family's feel; one per film.
- **Texture:** grain, vignette, scanlines, gradients: sparingly and consistently.

## Style frames
Before building every scene, render 2-3 stills in the chosen style (a headline scene, a
UI scene, the end card) with `contact_sheet.py` and show them. Changing a theme is cheap
now and expensive after 15 scenes.

## Warnings from experience
- 3D-extruded, metallic type (a "3D logo") tends to look cheap next to good flat type;
  one user rejected it outright. If someone wants it, render a style frame first.
- A single repeated scene pattern (headline, then panel, then headline...) reads as a
  slideshow in any style. Vary techniques per scene (`references/techniques.md`).
