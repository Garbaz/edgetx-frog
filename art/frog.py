"""The frog outline (50 x 32, without pupils and mouth: those are in faces.py).
Drawn as the left half, columns 0..24 (24 = the axis), mirrored to the right half."""

# head, rows 0..14: the black columns of each row; the skin outline flows over the eyes
HEAD = {
    0:  [15, 16, 17, 18, 19],                 # eye: its own bulge on top of the head
    1:  [14, 20],
    2:  [13, 21],
    3:  [13, 17, 18, 21],                     # pupil (wide, frog-like) with highlight at col 16
    4:  [13, 15, 16, 17, 18, 19, 21],
    5:  [13, 16, 17, 18, 21],
    6:  [13, 21, 22, 23, 24],                 # head top meets the eye from the inside
    7:  [14, 20],
    8:  [13, 15, 16, 17, 18, 19],             # eye bottom; head side starts below the eye
    9:  [13, 22],                             # nostril
    10: [12],                                 # cheek rounds outwards
    11: [12, 14],                             # mouth corner reaching into the cheek
    12: [12, 15, 16, 17, 18, 19],             # mouth, only a slight curve
    13: [13, 20, 21, 22, 23, 24],
    14: [14],                                 # jaw into the neck
}

# lower body, rows 14..28 (as point lists): front arms and hind legs, like a sitting frog seen from the front:
# a slim upright knee with a subtle fold beside the body, the shank and short toes on the ground
ARM = ([(15, y) for y in range(14, 20)] + [(14, y) for y in range(20, 26)] +
       [(17, 15)] + [(18, y) for y in range(16, 20)] + [(17, y) for y in range(20, 26)])
KNEE = ([(10, 15), (11, 15), (9, 16), (12, 16), (8, 17), (13, 17), (14, 18),           # rounded top
         (7, 18), (7, 19), (7, 20), (7, 21), (7, 22), (7, 23), (7, 24)]                # slim upright knee
        + [(x, 25) for x in range(7, 14)]                                       # shank on the ground
        + [(11, 21), (12, 22), (12, 23)])                                       # subtle fold
TOES = [(6, 26), (4, 27), (5, 27), (8, 26), (7, 27), (8, 27)]   # two toes: stem + 2 px pad, like the hands
HAND = [(13, 26), (12, 27), (10, 28), (11, 28),                                       # fingers fan out wide
        (15, 26), (15, 27), (14, 28), (15, 28),
        (16, 26), (17, 27), (17, 28), (18, 28),
        (18, 26), (19, 27), (20, 28), (21, 28)]
BELLY = [(x, 26) for x in range(20, 25)]
def half(points, y0, h):
    g = [['.'] * 25 for _ in range(h)]
    for x, y in points: g[y - y0][x] = '#'
    return [''.join(r) for r in g]

def build():
    head = [''.join('#' if x in cols else '.' for x in range(25)) for _, cols in sorted(HEAD.items())]
    body = half(ARM + KNEE + TOES + HAND + BELLY, 14, 15)
    body = body[:1] * 3 + body[1:]                 # a tad taller: repeat the neck row (only vertical lines there)
    return [r + r[::-1] for r in head + body]
