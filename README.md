# EdgeTX FROG Telemetry Screen

A telemetry screen for EdgeTX radios with a 128×64 B&W display, for Betaflight quads over ELRS/CRSF. It shows:

- the VTX power (top left), asked from Betaflight over the link; `--` while it doesn't answer
- the link quality (left): left half TQly (telemetry reaching the radio), right half RQly (control reaching the
  drone), a pulse climbing it while linked; it flashes below the model's "RF signal low" threshold
- the drone battery (right)
- a frog whose mood follows the flight, with the flight mode in a box below it (dashed while arming is blocked)
- the radio battery, the clock and the flight timer along the bottom

![preview](readme.webp)

The frog, most urgent first:

| Mood | When | |
|---|---|---|
| asleep | no link | eyes closed, z's rising |
| dizzy | failsafe, link critical, arming blocked | spiral eyes |
| anxious | something flashes: drone or radio battery low, link weak | glances at it, sweats |
| excited | armed | grins, hops with the throttle, hunts a fly |
| resting | disarmed | smiles |

## Install

1. Copy `SCRIPTS/TELEMETRY/frog.lua` to the same path on the radio's SD card.
2. On the radio, go to Model → Telemetry → Screens, set a screen to *Script* and select `frog`.

It is developed on a RadioMaster Pocket with EdgeTX 2.12.

The VTX power comes from Betaflight's `MSP2_GET_VTX_DEVICE_STATUS` over MSP-over-CRSF, which ELRS passes through;
Betaflight's CRSF telemetry itself has no VTX sensor. It is only asked while the screen is shown.

## Development

Needs [uv](https://docs.astral.sh/uv/). The pixel art is drawn in Python in `art/`: the frog and its face parts
(`frog.py`, `faces.py`), the link meter and the radio battery (`gauges.py`); `art/sprites_lua.py` writes it into
the generated block of `frog.lua`. `sim/` renders the script in a reproduction of EdgeTX's B&W display (including
the drone's MSP replies) and runs layout, centring and symmetry checks.

```sh
uv run build.py               # regenerate the sprites in frog.lua, render the previews and readme.webp, run the checks
uv run sim/render.py --help   # one-off renders of single states and frames, animation info
```

The fonts in `sim/fonts/` come from EdgeTX (GPL-2.0).
