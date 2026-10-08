# Blender hero shots (optional)

## When
For **physical products and devices**: a laptop/phone/tablet with the UI on screen, a
gadget, packaging, a hardware render. Blender gives real glass and metal, studio
shadows, reflections, depth of field. One or two hero shots per film is plenty
(a reveal, a finale).

Not for UI (CSS-3D keeps it sharp and animated) and usually not for type: extruded
metallic lettering tends to look cheap beside good flat type. If a style calls for it,
render a style frame first.

## Setup
- Blender 4.2+ (tested with 5.2 LTS). Installing it needs the user's OK. Windows:
  `winget install BlenderFoundation.Blender` (winget may live only at
  `%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe`; the installer raises a UAC prompt
  the user must approve). macOS: `brew install --cask blender`.
- Scripts run headless: `blender -b -P script.py -- args`. No MCP is needed; headless
  scripts are more reliable and repeatable than driving the UI.

## The device shot (scripts/blender_product_shot.py)
A laptop built from bevelled primitives with any image on its screen, a studio light
rig and a slow camera orbit. Parameters: `--screen`, `--out`, `--frames`, `--samples`,
`--shift-x` (lens shift to leave room for text), `--orbit`, `--radius`.
```
blender -b -P scripts/blender_product_shot.py -- --screen public/shots/screen.png --out public/shots/device --frames 1,65,130
```
- Render 3 test frames (start/middle/end), look, then the full range in the background.
  ~3 s/frame at 64 samples + OptiX on a laptop RTX 4050; long jobs may hit a 10-minute
  background limit: render in frame chunks and resume missing frames.
- Screen image 16:10 (1920×1200); pad a 16:9 UI with its own edge colours, don't crop.
- In the edit: `<ImageSeq dir="shots/device" count={130} speed={0.5} />`; nudge
  position/scale in the edit rather than re-rendering.
- Match the film's style: change the materials (aluminium colour, floor, light colours,
  background) to the theme; a light style wants a white seamless backdrop and soft
  shadows instead of a black mirror floor.
- For other products (phone, box, object), adapt the `build()` function: primitives +
  bevel modifiers, or import the user's model (`bpy.ops.wm.obj_import` / glTF import).

## Lessons baked in
- **Light linking** (`light.light_linking.receiver_collection`): rim/fill lights light
  only the product; otherwise a mirror floor shows them as white slabs.
- **AgX "Punchy"** keeps screens colourful; emissive screens need strength ~1.9.
- Blender 4.4+ keeps keyframes in layered actions; the script handles both APIs.
