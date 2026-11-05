"""Procedural 1-bit frog (front view, sitting) for a 128x64 LCD."""
import math
from PIL import Image, ImageDraw
W, H = 49, 30
C = 24                                   # vertical symmetry axis

def grid(v=0): return [[v]*W for _ in range(H)]
def ell(m, cx, cy, rx, ry, v=1):
    for y in range(H):
        for x in range(W):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0: m[y][x] = v
def rect(m, x0, y0, x1, y1, v=1):
    for y in range(max(0,y0), min(H,y1+1)):
        for x in range(max(0,x0), min(W,x1+1)): m[y][x] = v
def outline(m):
    o = grid()
    for y in range(H):
        for x in range(W):
            if m[y][x]:
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                    X, Y = x+dx, y+dy
                    if not (0 <= X < W and 0 <= Y < H) or not m[Y][X]:
                        o[y][x] = 1; break
    return o
def mirror_pts(pts): return pts + [(2*C - x, y) for x, y in pts]

def frog(texture=True):
    sil = grid()
    ell(sil, C, 10, 12.5, 6.5)                      # head
    for ex in (C-9, C+9): ell(sil, ex, 5.5, 5.2, 5.2)   # eye bulges
    ell(sil, C, 19, 10.5, 9)                        # body
    for tx in (C-14, C+14): ell(sil, tx, 21, 6, 5.5)    # hind thighs
    for fx in (C-19, C+19): ell(sil, fx, 27.5, 5.5, 1.6)  # hind feet on the ground
    for lx in (C-6, C+6): rect(sil, lx-1, 17, lx+1, 27)   # front legs
    g = outline(sil)
    # eyes: rim, big pupil, highlight
    for ex in (C-9, C+9):
        eye = grid(); ell(eye, ex, 5.5, 4.3, 4.3)
        for y in range(H):
            for x in range(W):
                if eye[y][x]: g[y][x] = 0
        o = outline(eye)
        pup = grid(); ell(pup, ex, 6, 2.6, 2.3)
        for y in range(H):
            for x in range(W):
                if o[y][x] or pup[y][x]: g[y][x] = 1
        g[5][ex-1] = 0                                # highlight
    # smile
    for x in range(C-8, C+9):
        y = 12 + round(1.3 * (1 - ((x-C)/8)**2)); g[y][x] = 1
    g[11][C-9] = g[11][C+9] = 1
    for x, y in mirror_pts([(C-2, 9)]): g[y][x] = 1     # nostrils
    # belly / throat line between the front legs
    for x in range(C-4, C+5):
        y = 15 + round(-0.9 * (1 - ((x-C)/4.5)**2)) + 1; g[y][x] = 1
    # front legs: inner edges, splayed toes with pads
    for lx in (C-6, C+6):
        for y in range(17, 28): g[y][lx-1] = g[y][lx+1] = 1
        for y in range(17, 28): g[y][lx] = 0
    for x, y in mirror_pts([(C-9, 29), (C-7, 29), (C-5, 29), (C-3, 29), (C-8, 28), (C-4, 28)]): g[y][x] = 1
    # hind feet toes
    for x, y in mirror_pts([(0, 28), (2, 29), (4, 29), (6, 29), (1, 27)]): g[y][x] = 1
    # skin texture (green areas): sparse staggered dots on head top and thighs
    if texture:
        skin = grid()
        ell(skin, C, 8, 10, 3.2)
        for tx in (C-14, C+14): ell(skin, tx, 20.5, 4, 3.5)
        for y in range(H):
            for x in range(W):
                if skin[y][x] and not g[y][x] and (x + 2*(y % 2)) % 4 == 0 and y % 2 == 0:
                    if all(not g[yy][xx] for yy in range(max(0,y-1), min(H,y+2)) for xx in range(max(0,x-1), min(W,x+2))):
                        g[y][x] = 1
    return g

def to_str(g): return [''.join('#' if v else '.' for v in r) for r in g]
def zoom(rowsets, path, sc=10):
    w = max(len(r[0]) for _, r in rowsets) + 2; h = sum(len(r) + 3 for _, r in rowsets)
    im = Image.new('RGB', (w*sc, h*sc), (178,196,170)); d = ImageDraw.Draw(im); y0 = 1
    for name, rows in rowsets:
        d.text((sc, (y0-1)*sc - 2), name, fill=(0,0,0))
        for y, r in enumerate(rows):
            for x, c in enumerate(r):
                if c == '#': d.rectangle([(x+1)*sc, (y0+y)*sc, (x+2)*sc-1, (y0+y+1)*sc-1], fill=(40,44,52))
        y0 += len(rows) + 3
    im.save(path)
if __name__ == '__main__':
    a, b = to_str(frog(True)), to_str(frog(False))
    zoom([('with skin texture', a), ('plain', b)], 'frog_core.png')
    print('\n'.join(a))
