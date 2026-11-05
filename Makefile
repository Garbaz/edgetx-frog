PY = .venv/bin/python
LUA = SCRIPTS/TELEMETRY/frog.lua

# regenerate the sprites in the script, render previews, run the layout checks
all: sprites preview check

sprites:
	$(PY) art/sprites_lua.py $(LUA) > /dev/null

preview:
	$(PY) sim/sim.py $(LUA) preview.png

check:
	$(PY) sim/check_layout.py $(LUA)
	$(PY) sim/check_center.py $(LUA)

.venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

.PHONY: all sprites preview check
