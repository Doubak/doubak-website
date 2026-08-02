#!/usr/bin/env python3
"""豆瓣备份器 logo family.

Three optical tiers over one geometry:
  small    16-20px    front hilum only, fatter channel, beans sit larger
  mid      24-96px    hilum on both beans
  display  128px+     both hilums, plus 豆 knocked out beside the front hilum
"""
import os, math, subprocess
from PIL import Image

OUT = "/mnt/user-data/outputs/doubak-logo"
os.makedirs(f"{OUT}/png", exist_ok=True)
GREEN, BEAN = "#2E963D", "#FFF4D8"

PATH = ("M 0 -5.2 C 2.3 -5.2 4 -2.9 4 0 C 4 2.9 2.3 5.2 0 5.2 "
        "C -2.1 5.2 -3.6 3 -3.6 0.1 C -3.6 -2.8 -2.1 -5.2 0 -5.2 Z")
SEG = [((0,-5.2),(2.3,-5.2),(4,-2.9),(4,0)), ((4,0),(4,2.9),(2.3,5.2),(0,5.2)),
       ((0,5.2),(-2.1,5.2),(-3.6,3),(-3.6,0.1)), ((-3.6,0.1),(-3.6,-2.8),(-2.1,-5.2),(0,-5.2))]
ROT = -20

# 豆 as supplied. Outer and inner subpaths wind opposite ways, so the 口 counter
# survives fill-rule nonzero and stays bean-coloured when used as a knockout.
DOU = ("M 65.02 30.16 L 18.57 30.16 L 18.57 46.18 L 65.02 46.18 Z "
       "M 9.11 21.78 L 74.39 21.78 L 74.39 54.56 L 9.11 54.56 Z "
       "M 2.23 4.65 L 81.27 4.65 L 81.27 13.04 L 2.23 13.04 Z "
       "M 24.34 55.95 C 27.8 60.79 30.89 66.63 33.63 73.45 L 50.16 73.45 "
       "C 53.43 68.18 56.31 62.34 58.78 55.95 L 68.28 59.21 "
       "C 65.79 64.6 63.11 69.36 60.27 73.45 L 83.5 73.45 L 83.5 81.74 "
       "L 0 81.74 L 0 73.45 L 24.34 73.45 C 22.1 69.04 19.2 64.3 15.59 59.21 Z")
DOU_W, DOU_CX, DOU_CY = 83.5, 41.75, 43.195

BACK_S, FRONT_S, DIST, AXIS = 1.00, 1.12, 7.6, math.radians(41)
HIL_X, HIL_W, HIL_H = -2.8, 1.15, 3.9      # hilum, bean-local
DOU_CENTRE, DOU_SIZE = 1.05, 4.0           # 豆 centre-x and width, bean-local


def fmt(v):
    s = f"{v:.4g}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def place(size, fill_frac):
    ca, sa = math.cos(math.radians(ROT)), math.sin(math.radians(ROT))
    b, f = (0.0, 0.0), (DIST*math.cos(AXIS), DIST*math.sin(AXIS))
    pts = []
    for c, s in ((b, BACK_S), (f, FRONT_S)):
        for p0, p1, p2, p3 in SEG:
            for i in range(25):
                t = i/24; u = 1-t
                x = (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0])*s
                y = (u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])*s
                pts.append((c[0] + x*ca - y*sa, c[1] + x*sa + y*ca))
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    k = size*fill_frac/max(x1-x0, y1-y0)
    ox, oy = size/2 - (x0+x1)/2*k, size/2 - (y0+y1)/2*k
    tf = lambda c, s: (f"translate({fmt(ox+c[0]*k)} {fmt(oy+c[1]*k)}) "
                       f"rotate({ROT}) scale({fmt(s*k)})")
    return tf(b, BACK_S), tf(f, FRONT_S), BACK_S*k, FRONT_S*k


def build(size=24, tier="mid", gap=0.95, fill_frac=0.66, radius_pct=0.25,
          tile=True, fill=BEAN, uid="a"):
    btf, ftf, bs, fs = place(size, fill_frac)
    hil = lambda t: (f'<rect x="{fmt(HIL_X)}" y="{fmt(-HIL_H/2)}" width="{fmt(HIL_W)}" '
                     f'height="{fmt(HIL_H)}" rx="{fmt(HIL_W/2)}" transform="{t}" fill="#000"/>')
    # 豆 rides inside the front bean's own transform, so it inherits the tilt
    g = DOU_SIZE/DOU_W
    glyph = (f'<path d="{DOU}" transform="{ftf} translate({fmt(DOU_CENTRE)} 0) '
             f'scale({fmt(g)}) translate({-DOU_CX} {-DOU_CY})" fill="#000"/>')

    back = hil(btf) if tier != "small" else ""
    front = hil(ftf) + ("\n    " + glyph if tier == "display" else "")
    plate = ((f'  <rect width="{size}" height="{size}"'
              + (f' rx="{fmt(size*radius_pct)}"' if radius_pct else "")
              + f' fill="{GREEN}"/>\n') if tile else "")

    # masks go on <g> wrappers, never on <path> directly -- cairosvg and some
    # older renderers get the mask region wrong when it sits on the path itself
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}" role="img" aria-label="豆瓣备份器"><title>豆瓣备份器</title>
  <mask id="b{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{size}" height="{size}">
    <rect width="{size}" height="{size}" fill="#fff"/>
    <path d="{PATH}" transform="{ftf}" fill="#000" stroke="#000" stroke-width="{fmt(2*gap/fs)}" stroke-linejoin="round"/>
    {back}
  </mask>
  <mask id="f{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{size}" height="{size}">
    <rect width="{size}" height="{size}" fill="#fff"/>
    {front}
  </mask>
{plate}  <g fill="{fill}">
    <g mask="url(#b{uid})"><path d="{PATH}" transform="{btf}"/></g>
    <g mask="url(#f{uid})"><path d="{PATH}" transform="{ftf}"/></g>
  </g>
</svg>
'''


masters = {
    "doubak-icon.svg":       build(24, "display", uid="a"),
    "doubak-icon-mid.svg":   build(24, "mid",     uid="n"),
    "doubak-icon-small.svg": build(16, "small",   gap=1.0, fill_frac=0.70, uid="s"),
    "doubak-mark.svg":       build(24, "display", tile=False, fill="currentColor", uid="m"),
    "doubak-maskable.svg":   build(24, "display", fill_frac=0.53, radius_pct=0, uid="k"),
}
for n, s in masters.items():
    open(f"{OUT}/{n}", "w").write(s)

# 豆 fragments below ~128px, so the mid tier covers everything under that
plan = [(16, "small"), (20, "small"), (24, "mid"), (32, "mid"), (48, "mid"),
        (64, "mid"), (96, "mid"), (128, "icon"), (180, "icon"),
        (192, "icon"), (256, "icon"), (512, "icon")]
src = {"small": "doubak-icon-small.svg", "mid": "doubak-icon-mid.svg",
       "icon": "doubak-icon.svg"}
def raster(src, dst, px):
    # librsvg, not cairosvg: cairosvg silently drops ALL masks in any document
    # that defines more than one, which this artwork does
    subprocess.run(["rsvg-convert", "-w", str(px), "-h", str(px),
                    f"{OUT}/{src}", "-o", f"{OUT}/png/{dst}"], check=True)

for px, t in plan:
    raster(src[t], f"icon-{px}.png", px)
raster("doubak-maskable.svg", "icon-maskable-512.png", 512)

ims = [Image.open(f"{OUT}/png/icon-{p}.png").convert("RGBA") for p in (16, 32, 48)]
ims[0].save(f"{OUT}/favicon.ico", format="ICO",
            sizes=[(16, 16), (32, 32), (48, 48)], append_images=ims[1:])
print("ok")
