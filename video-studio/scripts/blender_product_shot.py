"""A photoreal laptop hero shot with your UI on its screen, built and rendered
from nothing (no .blend file). Blender 4.2+ / 5.x, headless.

    blender -b -P blender_product_shot.py -- --screen public/shots/screen.png --out public/shots/laptop
        [--frames 1-130] [--samples 64] [--shift-x -0.13] [--orbit -44,-22] [--radius 10.9,10.0]

--screen: a 16:10 image (e.g. 1920x1200) of the UI to show; pad a 16:9 desktop with its
          own top/bottom colours rather than cropping panels off.
--shift-x: lens shift; negative puts the laptop right of centre (room for text on the left).
--orbit / --radius: camera azimuth and distance at the first and last frame (slow orbit).
Frames: <out>/0001.jpg ..., 1920x1080, 30 fps. Use ImageSeq in the kit; a 130-frame orbit
played at speed 0.5 fills ~8.7 s.

Use Blender for PRODUCTS (devices, objects), not for type or logos: extruded 3D text
read as cheap next to good flat type, and a user rejected it outright.
Lessons baked in:
- Light linking: rim/fill lights only light the laptop; otherwise the mirror floor shows
  them as huge white slabs.
- AgX "Punchy" look keeps colour; default looks wash emissive screens grey. Emission ~1.9.
- ~3 s/frame at 64 samples + OptiX denoise on an RTX 4050 laptop GPU.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def args():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opt = {"screen": "public/shots/screen.png", "out": "public/shots/laptop", "frames": "1-130", "samples": "64",
           "shift-x": "-0.13", "orbit": "-44,-22", "radius": "10.9,10.0"}
    for k, v in zip(a[::2], a[1::2]):
        opt[k.lstrip("-")] = v
    fr = []
    for part in opt["frames"].split(","):
        lo, _, hi = part.partition("-")
        fr += list(range(int(lo), int(hi or lo) + 1))
    opt["frames"] = fr
    return opt


def lin(hex_):
    c = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return (*[x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c], 1.0)


def set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def fresh_scene(samples):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for kind in ("OPTIX", "CUDA", "HIP", "METAL"):
        try:
            prefs.compute_device_type = kind
            break
        except TypeError:
            continue
    (prefs.refresh_devices if hasattr(prefs, "refresh_devices") else prefs.get_devices)()
    for d in prefs.devices:
        d.use = d.type != "CPU"
    sc.cycles.device = "GPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPTIX"
    except TypeError:
        sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.render.resolution_x, sc.render.resolution_y, sc.render.fps = 1920, 1080, 30
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    for vt in ("AgX", "Filmic"):
        try:
            sc.view_settings.view_transform = vt
            break
        except TypeError:
            continue
    for look in ("AgX - Punchy", "AgX - Medium High Contrast", "Medium High Contrast"):
        try:
            sc.view_settings.look = look
            break
        except TypeError:
            continue
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.0
    return sc


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def target(name, loc):
    ob = bpy.data.objects.new(name, None)
    ob.location = loc
    return link(ob)


def track(ob, tgt):
    c = ob.constraints.new("TRACK_TO")
    c.target, c.track_axis, c.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"


def area(name, loc, size, size_y, power, color, tgt):
    light = bpy.data.lights.new(name, "AREA")
    light.shape = "RECTANGLE"
    light.size, light.size_y, light.energy, light.color = size, size_y, power, color
    ob = link(bpy.data.objects.new(name, light))
    ob.location = loc
    track(ob, tgt)
    return ob


def only_lights(light, objects):
    coll = bpy.data.collections.new(light.name + "_receivers")
    for ob in objects:
        coll.objects.link(ob)
    light.light_linking.receiver_collection = coll


def principled(name, base, metallic=0.0, rough=0.5, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = base
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    set_input(p, ("Coat Weight", "Clearcoat"), coat)
    return m


def box(name, dims, loc, mat, bevel=0.04, segments=6, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = dims
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        mod = ob.modifiers.new("Bevel", "BEVEL")
        mod.width, mod.segments, mod.limit_method = bevel, segments, "ANGLE"
    for poly in ob.data.polygons:
        poly.use_smooth = True
    ob.data.materials.append(mat)
    if parent:
        ob.parent = parent
    return ob


def fcurves(action):
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    out = []
    for layer in getattr(action, "layers", []):                # Blender 4.4+ layered actions
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                out += list(bag.fcurves)
    return out


def orbit(center, radius, az, el):
    a, e = math.radians(az), math.radians(el)
    return Vector(center) + Vector((radius * math.sin(a) * math.cos(e), -radius * math.cos(a) * math.cos(e),
                                    radius * math.sin(e)))


def build(opt):
    W, D, T, H = 3.2, 2.2, 0.085, 2.08
    alu = principled("Aluminium", lin("#3b3d42"), 1.0, 0.34)
    keys = principled("Keys", lin("#0b0b0c"), 0.0, 0.55)
    glass = principled("Bezel", lin("#050505"), 0.0, 0.08, coat=1.0)
    pad = principled("Trackpad", lin("#35373c"), 1.0, 0.22)

    box("Base", (W, D, T), (0, 0, T / 2), alu, bevel=0.045)
    key = box("Key", (0.185, 0.185, 0.018), (-1.26, 0.02, T + 0.004), keys, bevel=0.012, segments=3)
    for axis, count in ((0, 13), (1, 5)):
        arr = key.modifiers.new(f"Array{axis}", "ARRAY")
        arr.count = count
        arr.relative_offset_displace = (1.13, 0, 0) if axis == 0 else (0, 1.13, 0)
    box("Trackpad", (1.35, 0.78, 0.004), (0, -0.62, T + 0.001), pad, bevel=0.01, segments=3)

    hinge = target("Hinge", (0, D / 2 - 0.02, T))
    hinge.rotation_euler = (math.radians(-12), 0, 0)             # lid open ~102 degrees
    box("Lid", (W, 0.055, H), (0, -0.0275, H / 2), alu, bevel=0.035, parent=hinge)
    box("Glass", (W - 0.06, 0.004, H - 0.06), (0, -0.057, H / 2), glass, bevel=0.0, parent=hinge)

    m = bpy.data.materials.new("Screen")
    m.use_nodes = True
    nt = m.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(Path(opt["screen"]).resolve()))
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.inputs["Strength"].default_value = 1.9
    gloss = nt.nodes.new("ShaderNodeBsdfPrincipled")
    gloss.inputs["Base Color"].default_value = (0, 0, 0, 1)
    gloss.inputs["Roughness"].default_value = 0.05
    add = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs[0], add.inputs[0])
    nt.links.new(gloss.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.0595, H / 2 + 0.03))
    scr = bpy.context.active_object
    scr.scale = (2.94, 2.94 / 1.6, 1)
    scr.rotation_euler = (math.radians(90), 0, 0)
    scr.data.materials.append(m)
    scr.parent = hinge

    body = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bpy.ops.mesh.primitive_plane_add(size=80, location=(0, 0, 0))
    bpy.context.active_object.data.materials.append(principled("Floor", lin("#050506"), 0.0, 0.18))

    aim = (0, 0.35, 0.95)
    tgt = target("Aim", aim)
    area("Key", (-3.2, -3.4, 5.2), 5, 3, 520, (1, 1, 1), tgt)
    for light in (area("RimR", (4.2, 4.0, 2.6), 4, 4, 700, (0.4, 0.8, 1.0), tgt),
                  area("RimL", (-4.2, 4.0, 2.2), 4, 4, 450, (0.65, 0.45, 1.0), tgt),
                  area("Fill", (0, -7, 1.0), 7, 1.2, 40, (1, 1, 1), tgt)):
        only_lights(light, body)

    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens, cam_data.shift_x = 50, float(opt["shift-x"])
    cam_data.dof.use_dof, cam_data.dof.focus_object, cam_data.dof.aperture_fstop = True, tgt, 4.0
    cam = link(bpy.data.objects.new("Cam", cam_data))
    track(cam, tgt)
    bpy.context.scene.camera = cam
    az0, az1 = (float(v) for v in opt["orbit"].split(","))
    r0, r1 = (float(v) for v in opt["radius"].split(","))
    last = max(opt["frames"])
    for frame, loc in ((1, orbit(aim, r0, az0, 17)), (last, orbit(aim, r1, az1, 13))):
        cam.location = loc
        cam.keyframe_insert("location", frame=frame)
    for fc in fcurves(cam.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"


def main():
    opt = args()
    sc = fresh_scene(int(opt["samples"]))
    build(opt)
    out = Path(opt["out"]).resolve()
    out.mkdir(parents=True, exist_ok=True)
    sc.frame_start, sc.frame_end = 1, max(opt["frames"])
    for f in opt["frames"]:
        sc.frame_set(f)
        sc.render.filepath = str(out / f"{f:04d}.jpg")
        bpy.ops.render.render(write_still=True)
        print(f"[shot] frame {f} -> {sc.render.filepath}", flush=True)


main()
