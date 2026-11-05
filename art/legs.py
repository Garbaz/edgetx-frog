"""Lower body (rows 14..28, left half cols 0..24): arms + hind legs, as point lists.
Hind leg like a sitting frog seen from the front: a rounded knee bulge beside the body, the long
hind foot fanning out along the ground from under it. Front feet with widely splayed fingers."""
ARM = ([(15, y) for y in range(14, 20)] + [(14, y) for y in range(20, 26)] +
       [(17, 15)] + [(18, y) for y in range(16, 20)] + [(17, y) for y in range(20, 26)])
KNEE = ([(10, 15), (11, 15), (9, 16), (12, 16), (8, 17), (13, 17), (14, 18),           # rounded top
         (7, 18), (7, 19), (7, 20), (7, 21), (7, 22), (7, 23), (7, 24)]                # slim upright knee
        + [(x, 25) for x in range(7, 14)]                                       # shank on the ground
        + [(11, 21), (12, 22), (12, 23)])                                       # subtle fold
SOLE = []
TOES = [(6, 26), (4, 27), (5, 27), (8, 26), (7, 27), (8, 27)]   # two toes: stem + 2 px pad, like the hands
HAND = [(13, 26), (12, 27), (10, 28), (11, 28),                                       # fingers fan out wide
        (15, 26), (15, 27), (14, 28), (15, 28),
        (16, 26), (17, 27), (17, 28), (18, 28),
        (18, 26), (19, 27), (20, 28), (21, 28)]
BELLY = [(x, 26) for x in range(20, 25)]
def rows():
    g = [['.'] * 25 for _ in range(15)]
    for x, y in ARM + KNEE + SOLE + TOES + HAND + BELLY:
        g[y - 14][x] = '#'
    return [''.join(r) for r in g]
