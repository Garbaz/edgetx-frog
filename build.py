"""Generate what frog.lua takes from elsewhere (its version, its sprites), render the previews, run the checks.

  uv run build.py                  # all four, in that order
  uv run build.py version check    # just some of them

The generated parts of frog.lua and readme.webp are committed; CI checks they are what this makes of the sources.
"""
import re, subprocess, sys, tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LUA = 'SCRIPTS/TELEMETRY/frog.lua'
VERSION_LINE = re.compile(r'^-- Version \S+, (\S+)$', re.M)


def stamp_version():
    """frog.lua's "-- Version X.Y.Z, <repo>" line: the version in pyproject.toml (scripts/release.py bumps it)."""
    version = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']['version']
    path = ROOT / LUA
    text = path.read_text()
    line = VERSION_LINE.search(text)
    if line is None: sys.exit(f'{LUA}: no "-- Version X.Y.Z, <repo>" line')
    path.write_text(text[:line.start()] + f'-- Version {version}, {line[1]}' + text[line.end():])


STEPS = {
    'version': [stamp_version],
    'sprites': [['art/sprites_lua.py', LUA]],
    'preview': [['sim/sim.py', LUA, 'preview.png']],
    'check':   [['sim/check_layout.py', LUA], ['sim/check_center.py', LUA], ['sim/check_behaviour.py', LUA]],
}

if __name__ == '__main__':
    for step in sys.argv[1:] or list(STEPS):
        if step not in STEPS: sys.exit(f'unknown step {step!r}, choose from {", ".join(STEPS)}')
        for cmd in STEPS[step]:
            if callable(cmd): cmd(); continue
            if subprocess.run([sys.executable, *cmd], cwd=ROOT).returncode:
                sys.exit(f'{step}: {cmd[0]} failed')
