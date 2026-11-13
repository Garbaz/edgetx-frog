"""Behaviour checks: what the screen shows for telemetry Betaflight can send, against what that telemetry means in
Betaflight (telemetry/crsf.c, sensors/battery.c, msp/msp.c) and the screen's design. Exits 1 if a case fails.

The cases read single pixels the design fixes: the drone voltage highlighted (low battery, while the warning blink is
on), the battery's fill, the mode box filled (armed), the VTX label."""
import sys
sys.path.insert(0, sys.path[0])
import sim
script = sys.argv[1]
T = 10                                                    # a tick with the warning blink on
def frame(tel, before=None):
    return sim.run(script, dict(tel, before=before) if before else tel, True, T)
def low(px):      return sum(px[y][x] for y in range(52, 64) for x in range(104, 128)) > 120   # voltage highlighted
def batt_fill(px): return px[47][113] == 1                                                    # bottom of the fill
def box_filled(px): return px[38][40] == 1
def vtx_label(px): return [tuple(px[y][10:30]) for y in range(1, 7)]
def volts(px): return [tuple(px[y][100:128]) for y in range(52, 64)]
def voltage_fits(px):
    ink = [x for y in range(52, 64) for x in range(100, 128) if px[y][x]]
    return min(ink) >= 100 and max(ink) <= 126                  # clear of the stopwatch, 1 px screen margin

base = sim.tel(99, 99, 8.2, 60, 3.5, 'AIR*')
cases = [
    # low drone battery: Betaflight's battery state, whatever the voltage
    ("3.5 V, Betaflight OK (not yet its warning delay) -> not low", not low(frame(dict(base, batt=0)))),
    ("3.5 V, Betaflight WARNING -> low", low(frame(dict(base, batt=1)))),
    ("3.3 V, Betaflight CRITICAL -> low", low(frame(dict(base, RxBt=3.3, batt=2)))),
    ("3.2 V Li-ion cell, Betaflight OK -> not low", not low(frame(dict(base, RxBt=3.2, batt=0)))),
    # without an MSP reply: low at Bat% 0, Betaflight's critical voltage or the capacity used up
    ("no MSP reply, Bat% 60 -> not low", not low(frame(dict(base, msp=False)))),
    ("no MSP reply, Bat% 0 -> low", low(frame(dict(base, msp=False, **{'Bat%': 0})))),
    ("Betaflight NOT_PRESENT, RxBt 3.8 -> no battery", not batt_fill(frame(dict(base, RxBt=3.8, batt=3)))),
    ("Betaflight OK, RxBt 3.8 -> battery filled", batt_fill(frame(dict(base, RxBt=3.8, batt=0)))),
    # the voltage per cell, from Betaflight's cell count; a pack voltage without it still fits
    ("4S, 16.8 V pack (RxBt the pack) -> shown as 4.2 V, like a 1S at 4.2 V",
     volts(frame(dict(base, RxBt=16.8, pack=16.8, cells=4, batt=0))) == volts(frame(dict(base, RxBt=4.2, batt=0)))),
    ("6S, no MSP reply, RxBt 25.2 V -> fits", voltage_fits(frame(dict(base, RxBt=25.2, msp=False)))),
    ("6S, no MSP reply, RxBt 19.8 V, Bat% 0 -> fits, highlighted",
     (lambda px: voltage_fits(px) and low(px))(frame(dict(base, RxBt=19.8, msp=False, **{'Bat%': 0})))),
    # "!FS!" says nothing about arming: the last known state holds
    ("!FS! after armed -> box filled", box_filled(frame(dict(base, FM='!FS!'), dict(base, FM='AIR')))),
    ("!FS! after disarmed -> box outlined", not box_filled(frame(dict(base, FM='!FS!'), dict(base, FM='AIR*')))),
    ("ACRO? (ready, GPS rescue unavailable) -> box outlined", not box_filled(frame(dict(base, FM='ACRO?')))),
    # VTX: pit mode from the VTX status, whatever the power level
    ("VTX pit flag at power index 1 -> PIT",
     vtx_label(frame(dict(base, vtx=1, pit=True))) == vtx_label(frame(dict(base, vtx=5)))
     and vtx_label(frame(dict(base, vtx=1))) != vtx_label(frame(dict(base, vtx=5)))),
]
# armed, then the link lost, then "!FS!": still armed
ses = sim.Session(script)
for t, tl in ((T - 60, dict(base, FM='AIR')), (T - 40, sim.tel(0, 0, 8.2)), (T - 20, dict(base, FM='!FS!'))):
    ses.frame(tl, t)
cases.append(("!FS! after armed and a lost link -> box filled", box_filled(ses.frame(dict(base, FM='!FS!'), T))))

for name, ok in cases: print('OK   ' if ok else 'FAIL ', name)
sys.exit(0 if all(ok for _, ok in cases) else 1)
