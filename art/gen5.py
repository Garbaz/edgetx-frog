"""Frog v5: head from gen4, lower body hand-drawn (left half, mirrored around col 24)."""
import gen4
from gen3 import zoom
HEAD = gen4.to_str(gen4.frog())[:14]           # rows 0..13
LOWER = [                                       # left half, cols 0..24 (col 24 = axis)
    "...............#.........",   # 14 neck
    "...............#.#.......",   # 15 shoulder, arm starts
    "..........###..#..#......",   # 16 thigh top
    "........##...###..#......",   # 17
    ".......#.......#..#......",   # 18
    "......#........#..#......",   # 19
    "......#.......#..#.......",   # 20
    "......#.......#..#.......",   # 21
    "......#.......#..#.......",   # 22
    ".......#......#..#.......",   # 23 thigh rounds off
    "....###########..#.......",   # 24 thigh closed against the arm
    "...#..........#..#.......",   # 25 hind toes start / ankle
    "..#.#######..#.##.#.#####",   # 26 wrist, belly closed
    "#.#.#.......#..#.#.#.....",   # 27 toes, fingers
    "##.##.....##..##.##.##...",   # 28 toe pads
]
def build():
    rows = []
    for r in HEAD: rows.append(r)
    import legs
    for r in legs.rows():
        assert len(r) == 25, (len(r), r)
        rows.append(r + r[::-1])
    return rows
if __name__ == '__main__':
    f = build(); zoom([('frog v5', f)], 'frog_core.png'); print('\n'.join(f))
