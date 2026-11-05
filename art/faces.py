"""Frog face parts. Coordinates are frog pixels of the LEFT half (x 0..24, frog is 50 wide),
mirrored to the right half automatically. The base frog is the resting frog minus pupils and mouth."""
import gen7

W = 50
def mirror(pts): return sorted(set(pts) | {(W - 1 - x, y) for x, y in pts})

PUPIL = [(17, 3), (18, 3)] + [(x, 4) for x in range(15, 20)] + [(x, 5) for x in range(16, 19)]
SMILE = [(14, 11)] + [(x, 12) for x in range(15, 20)] + [(x, 13) for x in range(20, 25)]

SMALL_PUPIL = [(x, y) for y in (3, 4, 5) for x in (16, 17, 18)]

SPIRAL = ["#####",
          "....#",
          "###.#",
          "#...#",
          "#####"]
def rot90(g): return [''.join(g[len(g) - 1 - j][i] for j in range(len(g))) for i in range(len(g[0]))]
def spiral_frames():
    frames, g = [], SPIRAL
    for _ in range(4):
        frames.append([(15 + x, 2 + y) for y, r in enumerate(g) for x, c in enumerate(r) if c == '#'])
        g = rot90(g)
    return frames

EYES = {
    'open':   PUPIL,                                                            # resting / armed
    'wide':   SMALL_PUPIL,                                                      # anxious: wide-eyed, small pupils
    'blink':  [(x, 4) for x in range(14, 21)],                                  # mid-blink: straight lid
    'closed': [(14, 4), (20, 4)] + [(x, 5) for x in range(15, 20)],             # asleep: curved lid
}
# armed, looking around: both pupils shift the same way (not mirrored, or the frog goes cross-eyed)
def gaze(dx, dy=0, p=PUPIL): return sorted({(x + dx, y + dy) for x, y in p} | {(W - 1 - x + dx, y + dy) for x, y in p})
GAZE = {'lookLeft': gaze(-1), 'lookRight': gaze(1),
        'atDrone': gaze(2, 1, SMALL_PUPIL), 'atRadio': gaze(-2, 1, SMALL_PUPIL)}  # anxious: glances at a low battery

MOUTHS = {
    'smile': SMILE,
    'grin':  [(14, 11)] + [(x, 12) for x in range(15, 25)] + [(x, 13) for x in range(17, 25)]   # armed: open grin
             + [(x, 14) for x in range(20, 25)],
    'grimace': ([(x, 11) for x in range(17, 25)] + [(x, 13) for x in range(17, 25)]    # anxious: clenched teeth
                + [(17, 12), (20, 12), (23, 12)]),
    'wavy':  [(14, 12), (15, 12), (18, 12), (19, 12), (22, 12), (23, 12),
              (16, 13), (17, 13), (20, 13), (21, 13), (24, 13)],
    'wide':  [(x, 12) for x in range(15, 25)],                                  # asleep, breathing in
    'snore': [(23, 11), (24, 11), (22, 12), (22, 13), (23, 14), (24, 14)],      # asleep, the open o of 😴
}

def base():
    rows = [list(r) for r in gen7.build()]
    for x, y in mirror(PUPIL + SMILE): rows[y][x] = '.'
    return [''.join(r) for r in rows]

def points(rows): return [(x, y) for y, r in enumerate(rows) for x, c in enumerate(r) if c == '#']
def to_runs(pts):
    pts, out = sorted(set(pts), key=lambda p: (p[1], p[0])), []
    for x, y in pts:
        if out and out[-1][1] == y and out[-1][0] + out[-1][2] == x: out[-1][2] += 1
        else: out.append([x, y, 1])
    return out
def lua_runs(pts): return '{ ' + ', '.join(f'{x}, {y}, {w}' for x, y, w in to_runs(pts)) + ' }'

def compose(eyes, mouth, frame=0):
    e = spiral_frames()[frame] if eyes == 'spiral' else EYES[eyes]
    return [''.join('#' if (c == '#' or (x, y) in set(mirror(e) + mirror(MOUTHS[mouth]))) else '.'
                    for x, c in enumerate(r)) for y, r in enumerate(base())]
