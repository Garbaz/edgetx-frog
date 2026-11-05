"""Frog v7: hand-placed head where the skin outline flows over the eyes (left half, mirrored)."""
import gen5
from gen3 import zoom
# left half, columns 0..24 (24 = axis); each entry lists the black columns of that row
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
def build():
    rows = []
    for y in range(len(HEAD)):
        half = ['.'] * 25
        for x in HEAD[y]: half[x] = '#'
        h = ''.join(half); rows.append(h + h[::-1])
    body = gen5.build()[14:]
    body = body[:1] * 3 + body[1:]                 # a tad taller: repeat the neck row (only vertical lines there)
    return rows + body
if __name__ == '__main__':
    f = build()
    zoom([('v7: skin flows over the eyes', f), ('v5 (before)', gen5.build())], 'frog_eyes.png', sc=12)
    print('\n'.join(f[:15]))
