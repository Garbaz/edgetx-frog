"""Measure the mode text's margins inside its fixed box, straight from the rendered pixels: equal, or (odd ink
width in the even box) the spare pixel on the right."""
import sys
sys.path.insert(0, sys.path[0])
from sim import run
script = sys.argv[1]
cases = [('AIR', 'armed'), ('AIR*', 'ready'), ('ANGL!', 'blocked'), ('HOR', 'armed'), ('!FS!', 'failsafe'),
         ('ALTH', 'armed'), ('CHIR', 'armed'), (None, 'no link')]
for fm, label in cases:
    tel = dict(rq=0, tx=7.9) if fm is None else {'rq': 99, 'tx': 7.9, 'TQly': 99, 'Bat%': 80, 'RxBt': 4.0, 'FM': fm}
    px = run(script, tel, True)
    rows = range(36, 56); cols = range(38, 90)   # between the VTX indicator and the drone %
    # box = outermost black frame in that region (dotted frames: use bounding box of black pixels)
    blk = [(x, y) for y in rows for x in cols if px[y][x]]
    x0 = min(x for x, _ in blk); x1 = max(x for x, _ in blk); y0 = min(y for _, y in blk); y1 = max(y for _, y in blk)
    filled = sum(px[y][x] for y in range(y0, y1+1) for x in range(x0, x1+1)) > 0.6 * (x1-x0+1) * (y1-y0+1)
    ink = [(x, y) for y in range(y0+1, y1) for x in range(x0+1, x1) if px[y][x] != filled]
    ix0 = min(x for x, _ in ink); ix1 = max(x for x, _ in ink); iy0 = min(y for _, y in ink); iy1 = max(y for _, y in ink)
    L, R, T, B = ix0 - x0 - 1, x1 - ix1 - 1, iy0 - y0 - 1, y1 - iy1 - 1
    ok = 'OK ' if (R - L in (0, 1) and T == B) else 'OFF'
    print(f'{ok} {label:9s} {str(fm):6s} box x{x0}-{x1} y{y0}-{y1}  margins L{L} R{R} T{T} B{B}')
