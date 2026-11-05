"""Frog v4: generated head (gen3) + hand-placed body lines, mirrored around x=24."""
import math, gen3
from gen3 import W, H, C, to_str, zoom

def line(g, x0, y0, x1, y1):
    n = max(abs(x1-x0), abs(y1-y0))
    for i in range(n+1):
        x = round(x0 + (x1-x0)*i/n); y = round(y0 + (y1-y0)*i/n)
        if 0 <= x < W and 0 <= y < H: g[y][x] = 1
def arc(g, cx, cy, rx, ry, a0, a1, clip=None):
    for k in range(361):
        t = math.radians(a0 + (a1-a0)*k/360)
        x = round(cx + rx*math.cos(t)); y = round(cy + ry*math.sin(t))
        if 0 <= x < W and 0 <= y < H and (clip is None or clip(x, y)): g[y][x] = 1

def frog():
    head = to_str(gen3.frog(False))
    g = [[1 if c == '#' else 0 for c in r[:C+1]] for r in head[:14]] + [[0]*(C+1) for _ in range(H-14)]
    L = [[0]*W for _ in range(H)]
    for y in range(H):
        for x in range(C+1): L[y][x] = g[y][x]
    # body side from cheek to shoulder
    line(L, 13, 13, 15, 15)
    # front arm: outer and inner edge, slightly splayed
    line(L, 15, 15, 13, 26)
    line(L, 18, 17, 16, 26); L[16][17] = 1
    # belly bottom between the arms
    arc(L, C, 22, 7.5, 5.5, 90, 160)
    # hind thigh, hidden behind the arm
    arc(L, 9, 21, 5.5, 5, 0, 360, clip=lambda x, y: x < 15 - (y-15)*2/11 - 0.5)
    # hind foot: long toes along the ground with pads
    line(L, 5, 26, 2, 27); line(L, 4, 26, 0, 28); line(L, 6, 26, 3, 29)
    for x, y in ((0, 27), (1, 29), (2, 29), (4, 29)): L[y][x] = 1
    # front hand: splayed fingers with pads
    for x0, x1 in ((13, 10), (14, 13), (16, 16), (16, 19)):
        line(L, x0, 26, x1, 28)
    for x, y in ((9, 28), (10, 29), (13, 29), (16, 29), (19, 29), (20, 28)): L[y][x] = 1
    for y in range(H):                                   # mirror
        for x in range(C): L[y][2*C - x] = L[y][x]
    return L[1:]                                         # drop empty top row

if __name__ == '__main__':
    f = to_str(frog())
    zoom([('frog v4', f)], 'frog_core.png')
    print(len(f[0]), 'x', len(f)); print('\n'.join(f))
