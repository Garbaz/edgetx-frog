# edgetx-frog

A telemetry screen for EdgeTX radios with a 128×64 B&W display, for Betaflight quads over ELRS/CRSF. It shows:

- the link quality (left)
- the drone battery (right)
- a frog whose mood and antics follow the flight, with the flight mode in a box below it
- the radio battery, the clock and the flight timer along the bottom

![preview](readme.webp)

## Install

1. Copy `SCRIPTS/TELEMETRY/frog.lua` to the same path on the radio's SD card.
2. On the radio, go to Model → Telemetry → Screens, set a screen to *Script* and select `frog`.

It is developed on a RadioMaster Pocket with EdgeTX 2.12.

## Development

The frog art and the face parts are drawn in Python in `art/`. `sim/` renders the script in a reproduction of EdgeTX's B&W display and runs layout and loop checks.

```sh
make                          # regenerate sprites in frog.lua, render previews (untracked) and readme.webp, run checks
uv run sim/render.py --help   # one-off renders of single states and frames, animation info
```

The fonts in `sim/fonts/` come from EdgeTX (GPL-2.0).
