# EdgeTX FROG Telemetry Screen

[![GitHub](https://img.shields.io/badge/GitHub-Garbaz%2Fedgetx--frog-blue?logo=github)](https://github.com/Garbaz/edgetx-frog)
[![Release](https://img.shields.io/github/v/release/Garbaz/edgetx-frog)](https://github.com/Garbaz/edgetx-frog/releases/latest)
[![CI](https://img.shields.io/github/actions/workflow/status/Garbaz/edgetx-frog/ci.yml?branch=main&label=CI)](https://github.com/Garbaz/edgetx-frog/actions/workflows/ci.yml)
[![EdgeTX](https://img.shields.io/badge/EdgeTX-2.12-blue)](https://edgetx.org)
[![Betaflight](https://img.shields.io/badge/Betaflight-2026.6-blue)](https://betaflight.com)
[![License](https://img.shields.io/github/license/Garbaz/edgetx-frog)](LICENSE)

A telemetry screen for EdgeTX radios with a 128×64 B&W display, for Betaflight quads over ELRS/CRSF. It shows:

- the VTX power (top left)
- the link quality (left: TQly, right: RQly)
- the drone battery and its voltage per cell (right)
- a frog whose mood follows the flight, with the flight mode in a box below it
- the radio battery, the clock and the flight timer along the bottom

![preview](readme.webp)

The frog sleeps without a link, gets dizzy in failsafe or while arming is blocked, glances anxiously at whatever
flashes (low batteries, a weak link) and hunts a fly while armed. The flight mode reads as on Betaflight's OSD, and the
drone battery counts as low when Betaflight warns about it, by the drone's own settings.

## Install

1. Download [`frog.lua`](https://github.com/Garbaz/edgetx-frog/releases/latest/download/frog.lua) from the
   [latest release](https://github.com/Garbaz/edgetx-frog/releases/latest) and copy it to `SCRIPTS/TELEMETRY/` on the
   radio's SD card.
2. On the radio, go to Model → Telemetry → Screens, set a screen to *Script* and select `frog`.

To update, replace the file. Its second line says which version it is; [CHANGELOG.md](CHANGELOG.md) says what changed.

Developed on a RadioMaster Pocket with EdgeTX 2.12, with a quad on a Betaflight 2026.6 pre-release.

## Development

Needs [uv](https://docs.astral.sh/uv/). The pixel art is drawn in Python in `art/`. `sim/` renders the script in a
reproduction of EdgeTX's B&W display and checks its layout and behaviour.

```sh
uv run build.py               # version and sprites into frog.lua, previews and readme.webp, checks
uv run sim/render.py --help   # one-off renders of single states and frames, animation info
```

Commit what `build.py` generates: CI fails if `frog.lua` or `readme.webp` differ from what it makes of the sources.

To release, note the changes under *Unreleased* in [CHANGELOG.md](CHANGELOG.md) and run
`uv run scripts/release.py patch|minor|major` on an up-to-date `main`. It bumps the version, builds, commits, tags and,
once confirmed, pushes; the tag makes GitHub Actions publish `frog.lua` as a release.

## License

GNU General Public License v2 or later, see [LICENSE](LICENSE).

The fonts in `sim/fonts/` come from [EdgeTX](https://github.com/EdgeTX/edgetx) (GPL-2.0-only).
