"""Speed-ramp a clip (velocity edits, slow-motion peaks) with ffmpeg; Remotion can't remap time itself.

    python speed_ramp.py in.mp4 out.mp4 --points 0:1.6,1.2:1.6,1.5:0.35,2.4:0.35,2.7:1.8,4:1.8 [--step 0.1] [--fps 30] [--interp]

--points  source_time:speed pairs (seconds in the source clip). Speed is interpolated linearly between
          points and the clip is cut to the first..last point. 2 = twice as fast, 0.35 = slow motion.
--step    how finely the ramp is stepped (s of source); 0.1 is smooth to the eye.
--interp  motion-interpolate first (minterpolate), for smooth slow motion from 30 fps phone clips. Slower.
Prints the output length and where every point lands in output time: put the slowest moment (the hit)
on a beat when you place the clip (references/editing.md §6). Video only; the film's music is separate.
"""
import argparse
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def speed_at(points, t):
    for (t0, s0), (t1, s1) in zip(points, points[1:]):
        if t0 <= t <= t1:
            return s0 + (s1 - s0) * (t - t0) / ((t1 - t0) or 1)
    return points[-1][1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src"); ap.add_argument("dst")
    ap.add_argument("--points", required=True)
    ap.add_argument("--step", type=float, default=0.1)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--interp", action="store_true")
    a = ap.parse_args()
    pts = sorted((float(t), float(s)) for t, s in (p.split(":") for p in a.points.split(",")))
    if len(pts) < 2 or any(s <= 0 for _, s in pts):
        sys.exit("need at least two points, speeds > 0")
    segs, t = [], pts[0][0]
    while t < pts[-1][0] - 1e-6:
        e = min(t + a.step, pts[-1][0])
        segs.append((t, e, speed_at(pts, (t + e) / 2)))
        t = e
    n = len(segs)
    pre = f"minterpolate=fps={a.fps * 4}:mi_mode=mci:mc_mode=aobmc:vsbmc=1," if a.interp else ""
    graph = [f"[0:v]{pre}split={n}" + "".join(f"[s{i}]" for i in range(n))]
    graph += [f"[s{i}]trim=start={s:.4f}:end={e:.4f},setpts=(PTS-STARTPTS)/{v:.4f}[v{i}]" for i, (s, e, v) in enumerate(segs)]
    graph.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps={a.fps},format=yuv420p[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-filter_complex", ";".join(graph), "-map", "[out]",
                    "-an", "-c:v", "libx264", "-crf", "16", "-preset", "medium", a.dst], check=True)
    out_t, marks = 0.0, {pts[0][0]: 0.0}
    for s, e, v in segs:
        out_t += (e - s) / v
        for pt, _ in pts:
            if s < pt <= e + 1e-9: marks[pt] = out_t
    print(f"{a.dst}: {out_t:.2f} s out of {pts[-1][0] - pts[0][0]:.2f} s of source")
    for pt, sp in pts:
        print(f"  source {pt:6.2f} s (speed {sp:g}) -> output {marks.get(pt, 0):6.2f} s")


if __name__ == "__main__":
    main()
