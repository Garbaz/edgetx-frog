"""Gauge art: the link meter's segments (lit and unlit) and the radio battery symbol, both on the left edge.

Left column, top to bottom: the VTX power (rows 1..6), the link meter (rows 13..47), the radio battery (rows 54..62,
bottom on the clock digits' row 62): 6 rows clear above and below the meter. The meter and the radio battery
both span x 2..18, the meter split by a blank column at x = 10."""

# radio battery: body 16 x 9 with 1 px rounding, nub 1 x 5 centred on it (as tall as the charge bar), 17 px wide
# like the meter
RADIO_BATT = [".##############..",
              "#..............#.",
              "#..............##",
              "#..............##",
              "#..............##",
              "#..............##",
              "#..............##",
              "#..............#.",
              ".##############.."]
RADIO_FILL = (2, 2, 12, 5)              # charge bar: x, y (relative to the symbol), max width, height; 1 px clear inside
RADIO_X, RADIO_Y = 2, 54

# link meter: LQ_SEGS segments per side (left half TQly, right half RQly), narrow at the bottom
LQ_SEGS, LQ_SEG_H, LQ_GAP = 6, 5, 1
LQ_HALF_W = list(range(3, 3 + LQ_SEGS))  # each segment 1 px wider (per half) than the one below: 3 .. 8 px,
                                        # 2 x 8 + the blank column = 17 px, the radio battery's width
LQ_AXIS = LQ_HALF_W[-1]                 # the blank column, relative to LQ_X
LQ_H = LQ_SEGS * LQ_SEG_H + (LQ_SEGS - 1) * LQ_GAP   # 35 rows
LQ_X, LQ_Y = 2, 13


def segment(w, h, side):
    """A w x h half segment, 1 px rounding on its outer corners. side -1: left half (outer edge at x = 0).
    Returns (lit, unlit): the filled shape, and its 1 px outline."""
    outer = 0 if side < 0 else w - 1
    lit = {(x, y) for y in range(h) for x in range(w) if not (x == outer and y in (0, h - 1))}
    unlit = {(x, y) for x, y in lit if (x, y - 1) not in lit or (x, y + 1) not in lit or (x - 1, y) not in lit or (x + 1, y) not in lit}
    return sorted(lit), sorted(unlit)


def segments():
    """{'lit': [side][k], 'unlit': [side][k]}: pixel lists in meter coordinates, k = 0 at the bottom, side 0 = left."""
    out = {'lit': [[], []], 'unlit': [[], []]}
    for side, sgn in enumerate((-1, 1)):
        for k, w in enumerate(LQ_HALF_W):
            y0 = LQ_H - LQ_SEG_H - k * (LQ_SEG_H + LQ_GAP)
            x0 = LQ_AXIS - w if sgn < 0 else LQ_AXIS + 1
            for kind, px in zip(('lit', 'unlit'), segment(w, LQ_SEG_H, sgn)):
                out[kind][side].append([(x0 + x, y0 + y) for x, y in px])
    return out


def pulse_rows():
    """The rows the liveness pulse steps through, bottom to top: only the segments' inner rows, so a lit segment
    keeps its outline (top and bottom edge) like an unlit one."""
    return [LQ_H - LQ_SEG_H - k * (LQ_SEG_H + LQ_GAP) + y for k in range(LQ_SEGS) for y in range(LQ_SEG_H - 2, 0, -1)]


def radio_battery():
    return [(x, y) for y, r in enumerate(RADIO_BATT) for x, c in enumerate(r) if c == '#']
