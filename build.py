"""Regenerate the sprites in frog.lua, render the previews, run the checks.

  uv run build.py                  # all three, in that order
  uv run build.py sprites check    # just some of them
"""
import subprocess, sys

LUA = 'SCRIPTS/TELEMETRY/frog.lua'
STEPS = {
    'sprites': [['art/sprites_lua.py', LUA]],
    'preview': [['sim/sim.py', LUA, 'preview.png']],
    'check':   [['sim/check_layout.py', LUA], ['sim/check_center.py', LUA], ['sim/check_loop.py', LUA]],
}

if __name__ == '__main__':
    for step in sys.argv[1:] or list(STEPS):
        if step not in STEPS: sys.exit(f'unknown step {step!r}, choose from {", ".join(STEPS)}')
        for cmd in STEPS[step]:
            subprocess.run([sys.executable, *cmd], check=True)
