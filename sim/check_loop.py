"""Every panel must repeat exactly after LOOP ticks (the armed panel runs a stateful scripted flight)."""
import sys
sys.path.insert(0, sys.path[0])
from sim import loop_frames, ANIM, LOOP, STEP
frames = loop_frames(sys.argv[1], loops=2)
n = LOOP // STEP
bad = [(ANIM[p][0], i * STEP) for i in range(n) for p in range(len(ANIM)) if frames[i][p] != frames[i + n][p]]
print('loop check:', f'all panels repeat exactly every {LOOP * 10} ms' if not bad else f'MISMATCH {bad[:5]}')
