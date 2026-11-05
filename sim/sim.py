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

def run(script, tel, blink_on, t=None):
    L = lua53.LuaRuntime(unpack_returned_tuples=True); g = L.globals(); lcd = LCD(blink_on); buzz = []
    def I(v):
        if isinstance(v, float):
            if v != int(v): raise ValueError(f"number has no integer representation: {v}")
            v = int(v)
        return v
    api = {
        'clear': lambda: None,
        'drawText': lambda x, y, t, f=0: lcd.text(I(x), I(y), str(t), int(f or 0)),
        'drawFilledRectangle': lambda x, y, w, h, f=0: lcd.frect(I(x), I(y), I(w), I(h), int(f or 0)),
        'drawRectangle': lambda x, y, w, h, f=0: lcd.rect(I(x), I(y), I(w), I(h), int(f or 0)),
        'drawPoint': lambda x, y, f=0: lcd.pt(I(x), I(y), int(f or 0)),
        'drawLine': lambda x1, y1, x2, y2, pat, f: (lcd.vline(I(x1), min(I(y1), I(y2)), abs(I(y2) - I(y1)) + 1, int(pat), int(f))
                                                   if x1 == x2 else lcd.hline(min(I(x1), I(x2)), I(y1), abs(I(x2) - I(x1)) + 1, int(pat), int(f))),
        'getLastLeftPos': lambda: lcd.last_left,
        'getLastRightPos': lambda: lcd.last_right,
    }
    g.lcd = L.table_from(api)
    for k, v in dict(BLINK=BLINK, INVERS=INVERS, RIGHT=RIGHT, CENTER=CENTER, LEFT=0, FORCE=FORCE, ERASE=ERASE,
                     SMLSIZE=SML, MIDSIZE=MID, DBLSIZE=DBL, BOLD=BOLD, SOLID=SOLID, DOTTED=DOTTED).items():
        g[k] = v
    streaming = tel.get('rq', 0) > 0
    def getValue(name):
        if name == 'tx-voltage': return tel['tx']
        if name == 'timer1': return tel.get('t', 0)
        if not streaming or name not in tel: return 0
        return tel[name]
    g.getValue = getValue
    g.getRSSI = lambda: (min(99, tel.get('rq', 0)), 45, 42)
    g.getGeneralSettings = lambda: L.table_from({'battMin': 6.6, 'battMax': 8.4, 'battWarn': 6.8})
    g.getDateTime = lambda: L.table_from({'hour': 15, 'min': 42})
    g.getTime = lambda: t if t is not None else (10 if blink_on else 80)
    g.playHaptic = lambda *a: buzz.append(a)
    mod = L.execute(open(script).read())
    mod.run(0)
    if buzz: print('  vibrate:', tel.get('FM'), buzz)
    return lcd.px

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

ARMED, READY, BLOCKED = tel(99, 98, 7.9, 87, 3.9, 'AIR', 83), tel(99, 99, 8.2, 100, 4.3, 'AIR*'), tel(80, 85, 7.6, 64, 4.0, 'ANGL!')
LOW, FAILSAFE, WEAK = tel(90, 92, 7.5, 18, 3.5, 'AIR', 312), tel(12, 30, 7.4, 41, 3.8, '!FS!', 401), tel(30, 64, 7.6, 58, 3.8, 'HOR', 200)
NOLINK = tel(0, 0, 6.7)
STATES = [  # name, telemetry, time in 10 ms ticks
    ("armed, acro", ARMED, 10), ("armed, blinking", ARMED, 405),
    ("disarmed, ready (z step 1)", READY, 10), ("disarmed, ready (z step 2)", READY, 70),
    ("disarmed, ready (z step 3)", READY, 130), ("disarmed, ready (z step 4)", READY, 190),
    ("disarmed, arming blocked", BLOCKED, 10),
    ("low drone battery: tired", LOW, 60), ("low drone battery: slow blink", LOW, 310),
    ("failsafe: dizzy (spin 1)", FAILSAFE, 10), ("failsafe: dizzy (spin 2)", FAILSAFE, 20),
    ("link critical: dizzy", WEAK, 40), ("no link, radio battery low", NOLINK, 10),
]
ANIM = [("awake (armed)", ARMED), ("asleep (disarmed)", READY), ("tired (low battery)", LOW), ("dizzy (failsafe)", FAILSAFE)]

if __name__ == '__main__':
    script, out = sys.argv[1], sys.argv[2]
    imgs = [labelled(to_img(run(script, tl, (t % 100) < 50, t)), n) for n, tl, t in STATES]
    sheet(imgs).save(out); print('saved', out)
    to_img(run(script, ARMED, True, 10), scale=8).save(out.replace('.png', '_big.png')); print('saved big')
    frames = []
    for t in range(0, 480, 5):                        # 4.8 s at 20 fps
        frames.append(sheet([labelled(to_img(run(script, tl, (t % 100) < 50, t), scale=3), n) for n, tl in ANIM]))
    gif = out.replace('.png', '_anim.gif')
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=50, loop=0); print('saved', gif)
