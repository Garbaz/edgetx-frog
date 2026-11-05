"""Render an EdgeTX B&W (128x64) Lua telemetry script to PNG, mimicking
radio/src/gui/128x64/lcd.cpp + gui/common/stdlcd/lcd_common.cpp (EdgeTX v2.12.4)."""
import sys, math
from lupa import lua53
from PIL import Image, ImageDraw
from fonts import FONTS

W, H = 128, 64
# flag bits (values are arbitrary here, the script only uses the names)
BLINK, INVERS, RIGHT, CENTER, FORCE, ERASE = 1, 2, 4, 8, 16, 32
SML, MID, DBL, BOLD = 0x100, 0x200, 0x400, 0x800
SOLID, DOTTED = 0xff, 0x55

class LCD:
    def __init__(s, blink_on):
        s.px = [[0] * W for _ in range(H)]; s.blink_on = blink_on
        s.last_left = s.last_right = 0
    def pt(s, x, y, att):
        if not (0 <= x < W and 0 <= y < H): return
        if att & FORCE: s.px[y][x] = 1
        elif att & ERASE: s.px[y][x] = 0
        else: s.px[y][x] ^= 1
    def hline(s, x, y, w, pat, att):
        for i in range(w):
            if pat & 1: s.pt(x + i, y, att); pat = (pat >> 1) | 0x80
            else: pat >>= 1
    def vline(s, x, y, h, pat, att):
        if pat == DOTTED and not (y % 2): pat = (~pat) & 0xff
        for j in range(h):
            if pat & (1 << ((y + j) % 8)): s.pt(x, y + j, att)
    def rect(s, x, y, w, h, att):
        s.vline(x, y, h, SOLID, att); s.vline(x + w - 1, y, h, SOLID, att)
        s.hline(x + 1, y + h - 1, w - 2, SOLID, att); s.hline(x + 1, y, w - 2, SOLID, att)
    def frect(s, x, y, w, h, att):
        for i in range(y, y + h): s.hline(x, i, w, SOLID, att)
    def font(s, f):
        return FONTS['DBL' if f & DBL else 'MID' if f & MID else 'SML' if f & SML else 'STD']
    def text(s, x, y, t, f):
        fnt = s.font(f); orig = x; width = 0
        if f & RIGHT: width = fnt.textw(t); x -= width
        elif f & CENTER: width = fnt.textw(t); x -= width // 2
        inv = blink = False
        if f & BLINK:
            if s.blink_on:
                if f & INVERS: inv = True
                else: blink = True
        elif f & INVERS: inv = True
        for c in t:
            cols = fnt.glyph(c); h = fnt.h
            seq = [None] + cols + [[False] * fnt.step]       # i=0 lead, glyph, trailing blank
            for i, col in enumerate(seq):
                if i == 0:
                    if x == 0 or not inv: continue
                    x -= 1; col = [False] * fnt.step
                for j in range(-1, h + 1):
                    if j < 0 or (j == h and fnt.name != 'SML'):
                        plot = False
                        if h >= 12: continue
                        if j < 0 and not inv: continue
                        if y + j < 0: continue
                    else:
                        plot = col[j] if j < len(col) else False
                    if inv: plot = not plot
                    if not blink: s.pt(x, y + j, FORCE if plot else ERASE)
                x += 1
        right = x + (1 if fnt.name == 'MID' else 0)
        if f & RIGHT: s.last_left, s.last_right = right - width, orig
        else: s.last_left, s.last_right = orig, right

VIBRATED = set()

class Session:
    """One Lua state across frames, like the radio: the script keeps its state between run() calls."""
    def __init__(self, script):
        self.L = lua53.LuaRuntime(unpack_returned_tuples=True); g = self.L.globals()
        self.tel, self.t, self.lcd, self.buzz = {}, 0, LCD(False), []
        def I(v):
            if isinstance(v, float):
                if v != int(v): raise ValueError(f"number has no integer representation: {v}")
                v = int(v)
            return v
        lcd = lambda: self.lcd
        api = {
            'clear': lambda: None,
            'drawText': lambda x, y, t, f=0: lcd().text(I(x), I(y), str(t), int(f or 0)),
            'drawFilledRectangle': lambda x, y, w, h, f=0: lcd().frect(I(x), I(y), I(w), I(h), int(f or 0)),
            'drawRectangle': lambda x, y, w, h, f=0: lcd().rect(I(x), I(y), I(w), I(h), int(f or 0)),
            'drawPoint': lambda x, y, f=0: lcd().pt(I(x), I(y), int(f or 0)),
            'drawLine': lambda x1, y1, x2, y2, pat, f: (lcd().vline(I(x1), min(I(y1), I(y2)), abs(I(y2) - I(y1)) + 1, int(pat), int(f))
                                                       if x1 == x2 else lcd().hline(min(I(x1), I(x2)), I(y1), abs(I(x2) - I(x1)) + 1, int(pat), int(f))),
            'getLastLeftPos': lambda: lcd().last_left,
            'getLastRightPos': lambda: lcd().last_right,
        }
        g.lcd = self.L.table_from(api)
        for k, v in dict(BLINK=BLINK, INVERS=INVERS, RIGHT=RIGHT, CENTER=CENTER, LEFT=0, FORCE=FORCE, ERASE=ERASE,
                         SMLSIZE=SML, MIDSIZE=MID, DBLSIZE=DBL, BOLD=BOLD, SOLID=SOLID, DOTTED=DOTTED).items():
            g[k] = v
        def getValue(name):
            tel = self.tel
            if name == 'tx-voltage': return tel['tx']
            if name == 'timer1': return tel.get('t', 0)
            if name == 'thr': return tel.get('thr', -1024)
            if not tel.get('rq', 0) or name not in tel: return 0
            return tel[name]
        g.getValue = getValue
        g.getRSSI = lambda: (min(99, self.tel.get('rq', 0)), 45, 42)
        g.getGeneralSettings = lambda: self.L.table_from({'battMin': 6.6, 'battMax': 8.4, 'battWarn': 6.8})
        g.getDateTime = lambda: self.L.table_from({'hour': 15, 'min': 42})
        g.getTime = lambda: self.t
        g.playHaptic = lambda *a: self.buzz.append(a)
        self.mod = self.L.execute(open(script).read())
    def frame(self, tel, t, blink_on=None):
        self.tel, self.t, self.buzz = tel, t, []
        self.lcd = LCD(bool(t & 64) if blink_on is None else blink_on)   # EdgeTX: BLINK_ON_PHASE = bit 6
        self.mod.run(0)
        if self.buzz and tel.get('FM') not in VIBRATED:
            VIBRATED.add(tel.get('FM')); print('  vibrate:', tel.get('FM'), self.buzz)
        return self.lcd.px

def run(script, tel, blink_on, t=None):
    return Session(script).frame(tel, 10 if t is None else t, None if t is not None else blink_on)

def to_img(px, scale=4):
    on, off = (40, 44, 52), (178, 196, 170)
    im = Image.new('RGB', (W * scale + 2 * scale, H * scale + 2 * scale), off)
    d = ImageDraw.Draw(im)
    for y in range(H):
        for x in range(W):
            if px[y][x]:
                d.rectangle([(x + 1) * scale, (y + 1) * scale, (x + 2) * scale - 1, (y + 2) * scale - 1], fill=on)
    return im

def tel(rq, tq, tx, bat=None, v=None, fm=None, t=0):
    d = dict(rq=rq, tx=tx, t=t)
    if rq: d.update({'TQly': tq, 'Bat%': bat, 'RxBt': v, 'FM': fm})
    return d

def labelled(im, name):
    c = Image.new('RGB', (im.width, im.height + 22), (255, 255, 255))
    ImageDraw.Draw(c).text((6, 4), name, fill=(0, 0, 0)); c.paste(im, (0, 22)); return c

def sheet(imgs, cols=2, pad=10):
    rows = math.ceil(len(imgs) / cols); w, h = imgs[0].size
    out = Image.new('RGB', (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), (255, 255, 255))
    for i, im in enumerate(imgs): out.paste(im, (pad + (i % cols) * (w + pad), pad + (i // cols) * (h + pad)))
    return out

def flight(t):
    """Scripted flight for the armed preview (t in ticks, loops every 1920):
    0.5 s arm; 1.0-7.5 s throttle 30..60 %, tilting up to 0.6 rad -> fly from the left, circling;
    7.5 s throttle down to 8 % (below the 10 % catch threshold, not zero) -> catch
    9.6-16.5 s throttle 85 %, tilting 0.9 rad -> fly from the right, circling fast;
    16.5 s disarm with the throttle still up -> catch, then the resting frog until re-arming"""
    s = (t % 1920) / 100
    thr, tilt = 0.0, 0.0
    if 1.0 <= s < 7.5: thr, tilt = 0.3 + 0.3 * (s - 1.0) / 6.5, 0.6 * min(1, (s - 1.0) / 3)
    elif 7.5 <= s < 9.6: thr = 0.08
    elif 9.6 <= s < 17.0: thr, tilt = 0.85, 0.9
    armed = 0.5 <= s < 16.5
    d = tel(99, 98, 7.9, 87, 3.9, 'AIR' if armed else 'AIR*', 83)
    d.update({'thr': -1024 + 2048 * thr, 'Ptch': tilt, 'Roll': 0.0})
    return d

def low_flight(t):
    d = flight(t); d.update({'Bat%': 18, 'RxBt': 3.5}); return d

ARMED, READY, BLOCKED = tel(99, 98, 7.9, 87, 3.9, 'AIR', 83), tel(99, 99, 8.2, 100, 4.3, 'AIR*'), tel(80, 85, 7.6, 64, 4.0, 'ANGL!')
LOW, FAILSAFE, WEAK = tel(90, 92, 7.5, 18, 3.5, 'AIR', 312), tel(12, 30, 7.4, 41, 3.8, '!FS!', 401), tel(30, 64, 7.6, 58, 3.8, 'HOR', 200)
NOLINK = tel(0, 0, 6.7)
LOW_READY = tel(90, 92, 7.5, 18, 3.5, 'AIR*')
STATES = [  # name, telemetry, time in 10 ms ticks (one frog beat = 40 ticks)
    ("disarmed: resting", READY, 100), ("disarmed: arming blocked", BLOCKED, 100),
    ("no link: breathing out, z", NOLINK, 10), ("no link: breathing out, z z", NOLINK, 50),
    ("no link: breathing out, z z Z", NOLINK, 90), ("no link: breathing in, z Z", NOLINK, 130),
    ("no link: breathing in, Z", NOLINK, 170), ("no link: breathing in", NOLINK, 210),
    ("anxious (low battery)", LOW_READY, 30), ("anxious: glance at the battery", LOW_READY, 70),
    ("anxious: sweat running down", LOW_READY, 100), ("anxious: shiver", LOW_READY, 185), ("armed, low battery", LOW, 100),
    ("failsafe: dizzy", FAILSAFE, 10), ("link critical: dizzy", WEAK, 20),
]
FLIGHT_STILLS = [  # name, time in ticks along the scripted flight (armed, one session)
    ("armed, throttle 0: calm", 75), ("throttle up: a fly comes in", 115), ("fly circling (in front)", 250),
    ("fly circling (behind the frog)", 330), ("throttle 8 %: tongue out", 755), ("tongue back with the fly", 770),
    ("gulp", 800), ("85 % throttle: big fast hops, fly from the right", 1000), ("fast circling", 1300),
    ("disarm: tongue out", 1655), ("disarm: gulp", 1700), ("disarmed: resting", 1800),
]
ANIM = [("armed: scripted flight", flight), ("disarmed: resting", READY), ("disarmed: arming blocked", BLOCKED),
        ("low battery: anxious", LOW_READY), ("low battery while flying", low_flight), ("failsafe", FAILSAFE), ("link critical", WEAK), ("no link: asleep, radio battery low", NOLINK)]
LOOP = 1920       # ticks (10 ms): 19.2 s = frog loop (4.8 s), EdgeTX blink (1.28 s) and the scripted flight
STEP = 5          # 20 fps

def at(tl, t): return tl(t) if callable(tl) else tl

def flight_frames(script, times):
    """Run the scripted flight in one session (like the radio) and return the frames at the given ticks."""
    ses, want, out = Session(script), set(times), {}
    for t in range(0, max(times) + 1, STEP):
        px = ses.frame(flight(t), t)
        if t in want: out[t] = px
    return [out[t] for t in times]

def loop_frames(script, scale=3, loops=1):
    """Frames of every ANIM panel over LOOP, after one warm-up loop so the stateful armed panel is seamless."""
    sessions = [Session(script) for _ in ANIM]
    for t in range(0, LOOP, STEP):
        for ses, (_, tl) in zip(sessions, ANIM): ses.frame(at(tl, t), t)
    frames = []
    for t in range(LOOP, LOOP * (1 + loops), STEP):
        frames.append([ses.frame(at(tl, t), t) for ses, (_, tl) in zip(sessions, ANIM)])
    return frames

if __name__ == '__main__':
    script, out = sys.argv[1], sys.argv[2]                       # out: preview.png
    # still sheet: the armed flight steps, then the individual animation steps of the other states
    fl = flight_frames(script, [t for _, t in FLIGHT_STILLS])
    imgs = [labelled(to_img(px), n) for (n, _), px in zip(FLIGHT_STILLS, fl)]
    imgs += [labelled(to_img(run(script, tl, True, t)), n) for n, tl, t in STATES]
    sheet(imgs).save(out.replace('.png', '_states.png')); print('saved', out.replace('.png', '_states.png'))
    to_img(fl[2], scale=8).save(out.replace('.png', '_big.png')); print('saved big')
    # seamless 19.2 s loop of every state, as animated PNG (APNG) and animated WebP
    frames = [sheet([labelled(to_img(px, scale=3), n) for px, (n, _) in zip(panels, ANIM)]) for panels in loop_frames(script)]
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=STEP * 10, loop=0, optimize=True)
    frames[0].save(out.replace('.png', '.webp'), save_all=True, append_images=frames[1:], duration=STEP * 10,
                   loop=0, lossless=True, method=4)
    print('saved', out, 'and', out.replace('.png', '.webp'), f'({len(frames)} frames)')
