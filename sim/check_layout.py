"""Pixel checks against the layout's design rules (see the comments in frog.lua): indicator margins, centring and
mirror symmetry, and that digit-count changes don't move anything else (values above the low warnings, which make the
frog glance). Prints the measurements, exits 1 if a rule is broken."""
import sys
sys.path.insert(0, sys.path[0])
from sim import run
script = sys.argv[1]
failed = []
def expect(ok, what):
    print(('OK   ' if ok else 'FAIL ') + what)
    if not ok: failed.append(what)
def T(bat=87, v=4.0, tx=7.9, rq=99, tq=99, t=83):
    return {'rq': rq, 'tx': tx, 't': t, 'TQly': tq, 'Bat%': bat, 'RxBt': v, 'FM': 'AIR'}
def bbox(px, xs, ys):
    pts = [(x, y) for y in ys for x in xs if px[y][x]]
    return min(x for x, _ in pts), max(x for x, _ in pts), min(y for _, y in pts), max(y for _, y in pts)
px = run(script, T(), True)
v = bbox(px, range(0, 30), range(0, 8)); m = bbox(px, range(0, 22), range(8, 52)); r = bbox(px, range(0, 22), range(52, 64))
b = bbox(px, range(100, 128), range(0, 51))
expect((v[0], v[2]) == (1, 1), f'vtx         x{v[0]}-{v[1]} y{v[2]}-{v[3]}  margins: left {v[0]}, top {v[2]} (1, 1)')
expect((m[0] + m[1]) == (r[0] + r[1]), f'link meter  x{m[0]}-{m[1]} y{m[2]}-{m[3]}  centre {(m[0]+m[1])/2}, '
                                       f'radio battery x{r[0]}-{r[1]} centre {(r[0]+r[1])/2} (the same)')
expect((b[0], b[1], b[2], b[3]) == (107, 125, 1, 50), f'battery     x{b[0]}-{b[1]} y{b[2]}-{b[3]} (x107-125 y1-50)')
f = bbox(px, range(30, 100), range(0, 34))
expect(f[0] + f[1] == 127, f'frog        x{f[0]}-{f[1]}  centre {(f[0]+f[1])/2} (63.5)')
c = bbox(px, range(20, 63), range(55, 64)); r = bbox(px, range(64, 105), range(55, 64))
expect(c[0] + r[1] == 127 and c[1] + r[0] == 127,
       f'clock group x{c[0]}-{c[1]}, timer group x{r[0]}-{r[1]}  mirrored about 63.5: {c[0]+r[1]} and {c[1]+r[0]} (127)')
def diff(a, b):
    return sorted({x for y in range(64) for x in range(128) if a[y][x] != b[y][x]})
for name, variants, field in (('drone', [T(bat=b, v=v) for b, v in ((100, 4.35), (52, 3.8), (7, 3.6))], (92, 127)),
                              ('radio %', [T(tx=v) for v in (8.4, 7.9, 6.8)], (1, 19))):
    base = run(script, variants[0], True); bad = set()
    for v in variants[1:]:
        cols = diff(base, run(script, v, True))
        bad |= {c for c in cols if not field[0] <= c <= field[1]}
    expect(not bad, f'{name}: pixels changed outside its own field: {sorted(bad) if bad else "none"}')
# symmetry: the link meter about its own centre (equal links), every mode box style about its own centre
from sim import NOLINK, READY, BLOCKED, ARMED
for name, tel in (('no link', NOLINK), ('lit', READY), ('partly lit', T(rq=60, tq=60))):
    px = run(script, tel, True)
    bad = sum(px[y][x] != px[y][m[0] + m[1] - x] for y in range(m[2], m[3] + 1) for x in range(m[0], m[1] + 1))
    expect(bad == 0, f'link meter mirror ({name}): {bad} mismatched pixels')
for name, tel in (('outline', READY), ('dotted', BLOCKED), ('filled', ARMED)):
    px = run(script, tel, True); x0, x1, y0, y1 = bbox(px, range(20, 100), range(35, 55))
    edge = [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1) if x in (x0, x1) or y in (y0, y1)]
    bad = sum(px[y][x] != px[y][x0 + x1 - x] or px[y][x] != px[y0 + y1 - y][x] for x, y in edge)
    expect(bad == 0, f'mode box border mirror ({name}): {bad} mismatched pixels')
sys.exit(1 if failed else 0)
