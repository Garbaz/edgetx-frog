"""Every animation must repeat exactly after LOOP ticks: frame(t) == frame(t + LOOP) for all states."""
import sys
sys.path.insert(0, sys.path[0])
from sim import run, ANIM, LOOP, STEP
script, bad = sys.argv[1], []
for name, tl in ANIM:
    for t in range(0, LOOP, STEP):
        if run(script, tl, True, t) != run(script, tl, True, t + LOOP) or run(script, tl, True, t) != run(script, tl, True, t + 7 * LOOP):
            bad.append((name, t))
print('loop check:', 'all states repeat exactly every', LOOP * 10, 'ms' if not bad else f'MISMATCH {bad[:5]}')
