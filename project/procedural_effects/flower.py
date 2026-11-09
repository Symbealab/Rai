#!/usr/bin/env python3
"""RAI — generative flower engine (procedural, deterministic, no credits).

Recreates the language of the flower reference: bundles of thin,
slightly-misregistered closed strands arranged in n-fold radial symmetry,
nested teardrop petal loops, a dense luminous core, additive light.

Order <-> chaos is controlled by continuous parameters (FlowerState):
    asym      non-n-periodic radius modulation (breaks symmetry)
    stretch   anisotropic radial distortion
    bifurc    petal splitting (frequency doubling)
    twist     vortex rotation, strongest near the core
    turb      flow-field displacement of every strand
    n_new / reorg   symmetry re-emerging at a new fold count (state G)

Usage:
    python3 flower.py sheet <out.png> [palette]          # states A-G contact sheet
    python3 flower.py morph <out.mp4> [palette] [secs]   # continuous A->G morph
palette: reference (magenta, as supplied) | lightning (blue/white, per brief)
"""
import subprocess
import sys
from dataclasses import dataclass, replace

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter

TAU = 2 * np.pi


@dataclass
class FlowerState:
    asym: float = 0.0
    stretch: float = 0.0
    bifurc: float = 0.0
    twist: float = 0.0
    turb: float = 0.0
    reorg: float = 0.0
    n_new: int = 13
    bloom: float = 1.0  # 0 = bud, 1 = open


STATES = {
    "A": FlowerState(),
    "B": FlowerState(asym=0.07),
    "C": FlowerState(asym=0.10, stretch=0.22, twist=0.12),
    "D": FlowerState(asym=0.10, stretch=0.10, bifurc=1.0, twist=0.15),
    "E": FlowerState(asym=0.14, bifurc=0.8, twist=1.25),
    "F": FlowerState(asym=0.30, stretch=0.15, bifurc=0.7, twist=0.8, turb=1.0),
    "G": FlowerState(asym=0.03, twist=0.1, turb=0.12, reorg=1.0),
}
STATE_NAMES = {
    "A": "Perfect symmetry", "B": "Slight asymmetry", "C": "Radial distortion",
    "D": "Petal bifurcation", "E": "Vortex formation", "F": "Chaotic morphology",
    "G": "Reorganized symmetry",
}

PALETTES = {
    # dark -> body -> hot core (density mapped)
    "reference": [(0.02, 0.0, 0.02), (0.55, 0.12, 0.38), (0.93, 0.45, 0.75), (1.0, 0.93, 0.98)],
    "lightning": [(0.0, 0.01, 0.04), (0.10, 0.25, 0.75), (0.45, 0.70, 1.0), (0.95, 0.97, 1.0)],
    "bridge":    [(0.01, 0.0, 0.04), (0.35, 0.18, 0.75), (0.70, 0.55, 1.0), (0.98, 0.95, 1.0)],
}


def lerp_state(a: FlowerState, b: FlowerState, u: float) -> FlowerState:
    f = lambda x, y: x + (y - x) * u
    return FlowerState(f(a.asym, b.asym), f(a.stretch, b.stretch), f(a.bifurc, b.bifurc),
                       f(a.twist, b.twist), f(a.turb, b.turb), f(a.reorg, b.reorg),
                       b.n_new, f(a.bloom, b.bloom))


def state_at(u: float) -> FlowerState:
    """u in [0,6] walks A..G continuously (smoothstep between keys)."""
    keys = list("ABCDEFG")
    u = float(np.clip(u, 0, 6))
    i = min(int(u), 5)
    w = u - i
    w = w * w * (3 - 2 * w)
    return lerp_state(STATES[keys[i]], STATES[keys[i + 1]], w)


class Flower:
    """A flower 'species' (fixed by seed); render(state, time) draws it."""

    def __init__(self, seed=7, n=11, rings=4, strands=4):
        self.rng = np.random.default_rng(seed)
        self.n, self.rings, self.strands = n, rings, strands
        r = self.rng
        self.asym_ph = r.uniform(0, TAU, 4)
        self.strand_ph = r.uniform(0, TAU, (64, 3))
        self.turb_k = r.normal(0, 1, (6, 2)) * 3.0
        self.turb_ph = r.uniform(0, TAU, 6)
        self.stretch_ang = r.uniform(0, np.pi)

    # -- radial field functions -------------------------------------------------
    def _warp(self, th, rr, s: FlowerState, time):
        """Apply order->chaos deformation to polar coords (rr normalised 0..1)."""
        k = np.arange(1, 4)[:, None]
        asym = (np.cos(k * th[None] + self.asym_ph[:3, None] + 0.3 * time) / k).sum(0)
        rr = rr * (1 + s.asym * asym)
        rr = rr * (1 + s.stretch * np.cos(2 * (th - self.stretch_ang)))
        th = th + s.twist * TAU * 0.5 * (1 - np.clip(rr, 0, 1.4) / 1.4) ** 2 + 0.05 * s.twist * time
        return th, rr

    def _turb(self, x, y, s: FlowerState, time):
        if s.turb <= 1e-4:
            return x, y
        dx = np.zeros_like(x)
        dy = np.zeros_like(y)
        for (kx, ky), ph in zip(self.turb_k, self.turb_ph):
            a = np.sin(kx * x + ky * y + ph + 0.7 * time)
            dx += ky * a  # divergence-free-ish (curl of a scalar potential)
            dy -= kx * a
        return x + s.turb * 0.012 * dx, y + s.turb * 0.012 * dy

    # -- geometry ---------------------------------------------------------------
    def curves(self, s: FlowerState, time=0.0):
        """Yield (points[N,2] in unit space ~[-1,1], weight)."""
        n = self.n
        bloom = 0.25 + 0.75 * s.bloom
        out = []
        th = np.linspace(0, TAU, 1400)

        def emit(th_, rr_, w, j):
            p = self.strand_ph[j % 64]
            # strand misregistration: the hand-drawn "bundle" look
            jitter = 0.012 * np.sin(3 * th_ + p[0]) + 0.008 * np.sin(5 * th_ + p[1] + time * 0.5)
            th2, rr2 = self._warp(th_, rr_ + jitter, s, time)
            x, y = rr2 * np.cos(th2), rr2 * np.sin(th2)
            x, y = self._turb(x, y, s, time)
            out.append((np.stack([x, y], 1) * bloom, w))

        def fold_profile(nf, th_):
            # mix original symmetry with bifurcated (2n) and reorganised (n_new) folds
            base = np.cos(nf * th_)
            bif = np.cos(2 * nf * th_ + 0.5)
            new = np.cos(s.n_new * th_)
            m = (1 - s.reorg) * ((1 - s.bifurc) * base + s.bifurc * bif) + s.reorg * new
            return m

        # 1. core: tight concentric rings -> white hot centre via density
        for j in range(9):  # dark pupil inside a white-hot annulus, as in the reference
            r0 = 0.045 + 0.007 * j
            emit(th, r0 + 0.003 * fold_profile(n, th), 0.9, j)
        # 2. scalloped rings (outer contour bundles)
        for ring in range(self.rings):
            r0 = 0.22 + 0.15 * ring
            amp = 0.025 + 0.012 * ring
            for k in range(self.strands):
                emit(th, r0 + amp * fold_profile(n, th) + 0.005 * k, 0.28, ring * 7 + k)
        # 3. petal loops: nested teardrops around each petal axis
        nf = n if s.reorg < 0.5 else s.n_new
        for i in range(nf):
            ang = TAU * i / nf
            for depth in range(4):
                L = 0.62 - 0.08 * depth
                Wd = (0.16 - 0.03 * depth) * (1 + 0.4 * s.bifurc)
                u = np.linspace(0, TAU, 360)
                # teardrop in local coords, from r=0.18 to r=0.18+L
                lr = 0.18 + L * (0.5 - 0.5 * np.cos(u))
                lw = Wd * np.sin(u) * (0.6 + 0.4 * np.sin(u / 2))
                th_l = ang + lw / np.maximum(lr, 0.05)
                if s.bifurc > 0.01:  # split into twin lobes
                    for sgn in (-1, 1):
                        emit(th_l + sgn * s.bifurc * 0.45 * np.pi / nf, lr, 0.3, i * 5 + depth + (sgn > 0) * 31)
                else:
                    emit(th_l, lr, 0.4, i * 5 + depth)
        # 4. spokes of small loops (the beaded rings in the reference)
        m = 3 * n
        for i in range(m):
            ang = TAU * i / m
            u = np.linspace(0, TAU, 120)
            emit(ang + 0.03 * np.cos(u) / 0.42, 0.42 + 0.03 * np.sin(u), 0.35, i)
        return out


def splat(img, pts, w):
    """Additive anti-aliased point splat of a densely resampled polyline."""
    H, W = img.shape
    seg = np.diff(pts, axis=0)
    L = np.hypot(seg[:, 0], seg[:, 1])
    nsub = np.maximum(1, np.ceil(L / 0.6)).astype(int)
    idx = np.repeat(np.arange(len(seg)), nsub)
    frac = np.concatenate([np.arange(k) / k for k in nsub])
    p = pts[idx] + seg[idx] * frac[:, None]
    x, y = p[:, 0], p[:, 1]
    ok = (x >= 0) & (x < W - 1) & (y >= 0) & (y < H - 1)
    x, y = x[ok], y[ok]
    x0, y0 = x.astype(int), y.astype(int)
    fx, fy = x - x0, y - y0
    for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
        np.add.at(img, (y0 + dy, x0 + dx), ww * w)


def render_density(W, H, flowers, time=0.0):
    """flowers: list of (Flower, FlowerState, cx, cy, radius_px, rotation)."""
    img = np.zeros((H, W), np.float32)
    for fl, st, cx, cy, R, rot in flowers:
        c, s_ = np.cos(rot), np.sin(rot)
        for pts, w in fl.curves(st, time):
            q = pts @ np.array([[c, s_], [-s_, c]])
            splat(img, np.stack([cx + q[:, 0] * R, cy + q[:, 1] * R], 1), w)
    return img


def tonemap(d, palette="reference", exposure=1.0):
    glow = d + 0.35 * gaussian_filter(d, 1.2) + 0.9 * gaussian_filter(d, 7.0)
    v = 1 - np.exp(-glow * 0.30 * exposure)
    stops = np.array(PALETTES[palette])
    pos = np.linspace(0, 1, len(stops))
    rgb = np.stack([np.interp(v, pos, stops[:, k]) for k in range(3)], -1)
    return (np.clip(rgb, 0, 1) ** (1 / 1.1) * 255).astype(np.uint8)


def frame(W, H, st, time, palette, species=None):
    species = species or Flower(seed=7, n=11)
    d = render_density(W, H, [(species, st, W / 2, H / 2, H * 0.42, 0.04 * time)], time)
    return tonemap(d, palette)


def sheet(out, palette="reference"):
    tw, th = 480, 480
    fl = Flower(seed=7, n=11)
    tiles = []
    for k in "ABCDEFG":
        im = Image.fromarray(frame(tw, th, STATES[k], 0.0, palette, fl))
        dr = ImageDraw.Draw(im)
        dr.text((12, 10), f"{k}  {STATE_NAMES[k]}", fill=(230, 230, 240), font=ImageFont.load_default(size=18))
        tiles.append(im)
    W = tw * 4
    canvas = Image.new("RGB", (W, th * 2), (0, 0, 0))
    try:  # 8th tile: crop of the supplied reference for side-by-side comparison
        ref = Image.open(__file__.rsplit("/", 1)[0] + "/flower_reference.jpg").convert("RGB")
        ref = ref.crop((110, 390, 540, 820)).resize((tw, th))
        ImageDraw.Draw(ref).text((12, 10), "REF  supplied artwork", fill=(230, 230, 240), font=ImageFont.load_default(size=18))
        tiles.append(ref)
    except OSError:
        pass
    for i, t_ in enumerate(tiles):
        canvas.paste(t_, ((i % 4) * tw, (i // 4) * th))
    canvas.save(out)


def morph(out, palette="reference", secs=10.0, W=960, H=540, fps=24):
    fl = Flower(seed=7, n=11)
    n = int(secs * fps)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-pix_fmt",
                          "yuv420p", "-crf", "16", out], stdin=subprocess.PIPE)
    for i in range(n):
        tt = i / fps
        u = 6 * i / (n - 1)
        st = replace(state_at(u), bloom=min(1.0, 0.15 + tt / 2.0))
        p.stdin.write(frame(W, H, st, tt, palette, fl).tobytes())
    p.stdin.close()
    p.wait()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, out = sys.argv[1], sys.argv[2]
    pal = sys.argv[3] if len(sys.argv) > 3 else "reference"
    if cmd == "sheet":
        sheet(out, pal)
    elif cmd == "morph":
        morph(out, pal, float(sys.argv[4]) if len(sys.argv) > 4 else 10.0)
