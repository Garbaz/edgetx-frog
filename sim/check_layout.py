"""Pixel checks: indicator margins, and that digit-count changes don't move anything else."""
import sys
sys.path.insert(0, sys.path[0])
from sim import run
script = sys.argv[1]
def T(bat=87, tx=7.9, rq=99, tq=99, t=83):
    return {'rq': rq, 'tx': tx, 't': t, 'TQly': tq, 'Bat%': bat, 'RxBt': 4.0, 'FM': 'AIR'}
def bbox(px, xs, ys):
    pts = [(x, y) for y in ys for x in xs if px[y][x]]
    return min(x for x, _ in pts), max(x for x, _ in pts), min(y for _, y in pts), max(y for _, y in pts)
px = run(script, T(), True)
m = bbox(px, range(0, 22), range(0, 48)); b = bbox(px, range(104, 128), range(0, 48))
print(f'link meter  x{m[0]}-{m[1]} y{m[2]}-{m[3]}  margins: left {m[0]}, top {m[2]}')
print(f'battery     x{b[0]}-{b[1]} y{b[2]}-{b[3]}  margins: right {127-b[1]}, top {b[2]}')
print('widths', m[1]-m[0]+1, b[1]-b[0]+1, ' heights', m[3]-m[2]+1, b[3]-b[2]+1)
f = bbox(px, range(30, 100), range(0, 34)); print(f'frog        x{f[0]}-{f[1]}  centre {(f[0]+f[1])/2}')
c = bbox(px, range(20, 63), range(55, 64)); r = bbox(px, range(64, 105), range(55, 64))
print(f'clock group x{c[0]}-{c[1]}, timer group x{r[0]}-{r[1]}  -> mirror check {c[0]+r[1]} and {c[1]+r[0]} (127 = symmetric)')
def diff(a, b):
    return sorted({x for y in range(64) for x in range(128) if a[y][x] != b[y][x]})
for name, variants, field in (('drone %', [T(bat=v) for v in (100, 52, 7)], (92, 127)),
                              ('radio %', [T(tx=v) for v in (8.4, 7.9, 6.75)], (1, 17))):
    base = run(script, variants[0], True); bad = set()
    for v in variants[1:]:
        cols = diff(base, run(script, v, True))
        bad |= {c for c in cols if not field[0] <= c <= field[1]}
    print(f'{name}: pixels changed outside its own field: {sorted(bad) if bad else "none"}')
