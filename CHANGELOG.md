# Changelog

All notable changes to the FROG telemetry screen. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The first release: a telemetry screen for EdgeTX radios with a 128×64 B&W display, for Betaflight over CRSF. It
  shows the VTX power, the link quality both ways, the drone battery with its voltage per cell, the radio battery, the
  clock, the flight timer, the flight mode, and a frog whose mood follows the flight.
- The flight mode reads as on Betaflight's OSD (`AIR`, `ANGL`, `HOR`, `RESC`, ...), in a box that is filled while
  armed and dotted while arming is blocked.
- The drone battery counts as low when Betaflight warns about it (`LOW BATTERY`, `LAND NOW`), by the drone's own
  settings, so it fits any battery chemistry and cell count. Without that from the drone, it counts as low at 0 %.
- A dotted battery when the drone has no battery or there is no link.
- VTX power and pit mode, asked from Betaflight over MSP.
- A double vibration every 2.4 s in failsafe, which logical switches can't do (the flight mode is text).

[Unreleased]: https://github.com/Garbaz/edgetx-frog/commits/main
