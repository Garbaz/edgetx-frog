"""Ad-hoc renders while iterating on the script, so they don't have to be rewritten every time.

  uv run sim/render.py frames BOTH_LOW 30 65 90             # frames of a state at the given ticks (10 ms)
  uv run sim/render.py frames low_flight 75 250 780 --scale 6 --cols 2 -o low.png
  uv run sim/render.py list                                 # the states and flight profiles to choose from
  uv run sim/render.py info readme.webp                     # size, frames, loop length of an animation
  uv run sim/render.py dark readme.webp 150 -o dark.png     # one frame on a dark background (transparency)

States are the telemetry constants in sim.py (READY, LOW_READY, ...) or the scripted flights (flight,
low_flight); every state runs in one session from t = 0, like the radio, so stateful animations are right.
"""
import argparse, struct, sys
sys.path.insert(0, sys.path[0])
import sim
from PIL import Image

SCRIPT = 'SCRIPTS/TELEMETRY/frog.lua'

def states():
    return {k: v for k, v in vars(sim).items()
            if (k.isupper() and isinstance(v, dict) and 'rq' in v) or k in ('flight', 'low_flight')}

def frames(args):
    tl = states()[args.state]
    ses, want, got = sim.Session(args.script), sorted(args.ticks), {}
    for t in range(0, want[-1] + 1):
        if t % sim.STEP and t not in want: continue       # same frame rate as the previews, plus the asked ticks
        px = ses.frame(sim.at(tl, t), t)
        if t in want: got[t] = px
    imgs = [sim.labelled(sim.to_img(got[t], args.scale), f'{args.state} t={t}') for t in args.ticks]
    sim.sheet(imgs, cols=args.cols).save(args.out); print('saved', args.out)

def webp_durations(path):
    b, i, out = open(path, 'rb').read(), 12, []
    while i < len(b):
        tag, size = b[i:i + 4], struct.unpack('<I', b[i + 4:i + 8])[0]
        if tag == b'ANMF': out.append(int.from_bytes(b[i + 20:i + 23], 'little'))
        i += 8 + size + (size & 1)
    return out

def info(args):
    im = Image.open(args.file)
    if args.file.endswith('.webp'): d = webp_durations(args.file)    # Pillow reports 0 for WebP frames
    else:
        d = []
        for i in range(getattr(im, 'n_frames', 1)): im.seek(i); d.append(im.info.get('duration', 0))
    print(f'{args.file}: {im.size[0]}x{im.size[1]} {im.mode}, {len(d)} frames, {sum(d)} ms')

def dark(args):
    im = Image.open(args.file); im.seek(args.frame)
    f = im.convert('RGBA'); bg = Image.new('RGBA', f.size, (13, 17, 23, 255)); bg.alpha_composite(f)
    bg.save(args.out); print('saved', args.out)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    f = sub.add_parser('frames'); f.add_argument('state'); f.add_argument('ticks', type=int, nargs='+')
    f.add_argument('--scale', type=int, default=4); f.add_argument('--cols', type=int, default=3)
    f.add_argument('-o', '--out', default='frames.png'); f.add_argument('--script', default=SCRIPT)
    sub.add_parser('list')
    i = sub.add_parser('info'); i.add_argument('file')
    d = sub.add_parser('dark'); d.add_argument('file'); d.add_argument('frame', type=int, nargs='?', default=0)
    d.add_argument('-o', '--out', default='dark.png')
    a = p.parse_args()
    if a.cmd == 'list': print(' '.join(states()))
    else: {'frames': frames, 'info': info, 'dark': dark}[a.cmd](a)
