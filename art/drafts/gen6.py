"""Frog v6: head and eyes as one silhouette (skin flows over the eyes), body from gen5."""
import math, gen5
from gen3 import zoom
W, C, HH = 49, 24, 15                     # head area height (rows 0..14)

def grid(): return [[0]*W for _ in range(HH)]
def ell(m, cx, cy, rx, ry):
    for y in range(HH):
        for x in range(W):
            if ((x-cx)/rx)**2 + ((y-cy)/ry)**2 <= 1.0: m[y][x] = 1
def outline(m):
    o = grid()
    for y in range(HH):
        for x in range(W):
            if m[y][x] and any(not (0 <= x+dx < W and 0 <= y+dy < HH) or not m[y+dy][x+dx]
                               for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                o[y][x] = 1
    return o

def head(v):
    sil = grid()
    ell(sil, C, 9.5, 12.5, 6.3)                        # head
    for s in (-1, 1):
        ell(sil, C + s*v['ex'], v['ey'], v['br'], v['br'] * v['bh'])   # eye bulge under the skin
    ell(sil, C, v['ey'] + 1.5, v['ex'] - 1, 2.8)          # skin bridge between the eyes
    g = outline(sil)
    for s in (-1, 1):
        cx, cy = C + s*(v['ex'] + v['eo']), v['ey'] - 0.3   # eyeball sits towards the outer side
        eye = grid(); ell(eye, cx, cy, v['er'], v['er'] * 0.92)
        for y in range(HH):
            for x in range(W):
                if eye[y][x]: g[y][x] = 0
        rim = outline(eye)
        pup = grid(); ell(pup, cx, cy + 0.2, v['pr'], v['pr'] * v['ph'])
        for y in range(HH):
            for x in range(W):
                if rim[y][x] or pup[y][x]: g[y][x] = 1
        g[round(cy) - 1][round(cx) - s] = 0              # highlight, towards the nose
        if v.get('lid'):                                 # upper eyelid fold
            for x in range(round(cx) - 2, round(cx) + 3):
                y = round(cy - v['er'] - 1 + 0.15 * (x - cx)**2)
                if 0 <= y < HH: g[y][x] = 1
    for x in range(C - 8, C + 9):                          # smile
        g[11 + round(1.3 * (1 - ((x - C)/8)**2))][x] = 1
    g[10][C-9] = g[10][C+9] = 1
    g[8][C-2] = g[8][C+2] = 1                              # nostrils
    return g

VARIANTS = {
    'A: eyes on top':        dict(ex=9,  ey=5,   br=5.6, bh=0.85, eo=0.0, er=3.4, pr=2.3, ph=0.75),
    'B: eyes to the side':   dict(ex=10, ey=5.5, br=5.2, bh=0.9,  eo=0.6, er=3.6, pr=2.4, ph=0.7),
    'C: B + eyelid fold':    dict(ex=10, ey=5.5, br=5.2, bh=0.9,  eo=0.6, er=3.4, pr=2.3, ph=0.7, lid=1),
}
def build(v):
    h = [''.join('#' if p else '.' for p in r) for r in head(v)]
    body = gen5.build()[14:]
    return h[:14] + body
if __name__ == '__main__':
    zoom([(n, build(v)) for n, v in VARIANTS.items()], 'frog_eyes.png', sc=12)
    for n, v in VARIANTS.items(): print(n); print('\n'.join(build(v)[:15])); print()
