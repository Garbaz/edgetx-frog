-- FROG A75C telemetry screen for the RadioMaster Pocket (EdgeTX, 128x64 B&W)
--
--  left:   link quality wedge (left half: TQly = what the radio receives,
--                              right half: RQly = what the drone receives)
--  center: frog on a lily pad - asleep while disarmed, awake while armed;
--          flight mode in a box below (filled while armed)
--  right:  drone battery (BETAFPV LAVA style) + Betaflight Bat%
--  bottom: radio battery + clock

local DRONE_LOW_V = 3.6   -- same threshold as the L01 vibration alarm (RxBt < 3.6 V)

local MODES = { AIR = "ACRO", ACRO = "ACRO", ANGL = "ANGLE", HOR = "HORIZ",
                CHIR = "CHIRP", PASS = "PASS", ALTH = "ALTH", POSH = "POSH",
                PHFL = "POSH", RTH = "RTH" }

local FROG_AWAKE = {
  "...#####...........#####...",
  "..#.....#.........#.....#..",
  ".#.......#.......#.......#.",
  ".#...##..#.......#...##..#.",
  ".#..###..#.......#..###..#.",
  ".#..###..#.......#..###..#.",
  ".#.......#########.......#.",
  "..#.....#.........#.....#..",
  "...#####...........#####...",
  "..##...................##..",
  ".##........#...#........##.",
  "##.......................##",
  "#....#...............#....#",
  "#.....#.............#.....#",
  "#......###.......###......#",
  "##........#######........##",
  ".##.....................##.",
  "..##...................##..",
  "...###...............###...",
  "....#####.........#####....",
  "...#.#.#############.#.#...",
}

local FROG_ASLEEP = {
  "...#####...........#####...",
  "..#.....#.........#.....#..",
  ".#.......#.......#.......#.",
  ".#.......#.......#.......#.",
  ".#.#...#.#.......#.#...#.#.",
  ".#..###..#.......#..###..#.",
  ".#.......#########.......#.",
  "..#.....#.........#.....#..",
  "...#####...........#####...",
  "..##...................##..",
  ".##........#...#........##.",
  "##.......................##",
  "#.........................#",
  "#.........................#",
  "#........#.......#........#",
  "##........#######........##",
  ".##.....................##.",
  "..##...................##..",
  "...###...............###...",
  "....#####.........#####....",
  "...#.#.#############.#.#...",
}

local FROG_DIZZY_A = {
  "...#####...........#####...",
  "..#.....#.........#.....#..",
  ".#..###..#.......#....#..#.",
  ".#.#...#.#.......#.##..#.#.",
  ".#.#.#.#.#.......#.#.#.#.#.",
  ".#.#..##.#.......#.#...#.#.",
  ".#..#....#########..###..#.",
  "..#.....#.........#.....#..",
  "...#####...........#####...",
  "..##...................##..",
  ".##........#...#........##.",
  "##.......................##",
  "#.........................#",
  "#.......##..##..##........#",
  "#......#..##..##..##......#",
  "##.......................##",
  ".##.....................##.",
  "..##...................##..",
  "...###...............###...",
  "....#####.........#####....",
  "...#.#.#############.#.#...",
}

local FROG_DIZZY_B = {
  "...#####...........#####...",
  "..#.....#.........#.....#..",
  ".#....#..#.......#..###..#.",
  ".#.##..#.#.......#.#...#.#.",
  ".#.#.#.#.#.......#.#.#.#.#.",
  ".#.#...#.#.......#.#..##.#.",
  ".#..###..#########..#....#.",
  "..#.....#.........#.....#..",
  "...#####...........#####...",
  "..##...................##..",
  ".##........#...#........##.",
  "##.......................##",
  "#.........................#",
  "#.......##..##..##........#",
  "#......#..##..##..##......#",
  "##.......................##",
  ".##.....................##.",
  "..##...................##..",
  "...###...............###...",
  "....#####.........#####....",
  "...#.#.#############.#.#...",
}

local SWEAT = {
  "..#..",
  ".#.#.",
  "#...#",
  "#...#",
  ".###.",
}

local ZZZ = {
  ".....####",
  "........#",
  ".......#.",
  "###...#..",
  "..#..####",
  ".#.......",
  "###......",
}

local LILY_PAD = {
  "......##############.....##########......",
  "...###..............#...#..........###...",
  ".##..................#.#..............##.",
  "#.......#.............#.........#.......#",
  ".##......#...................#........##.",
  "...####...#.................#......###...",
  ".......###########################.......",
}

local BOLT = {
  "..##",
  ".##.",
  "##..",
  "####",
  "..##",
  ".##.",
  "##..",
}

-- turn a sprite (list of strings) into horizontal runs, once at load time
local function runs(sprite)
  local r = {}
  for y, row in ipairs(sprite) do
    local x = 1
    while true do
      local s, e = string.find(row, "#+", x)
      if not s then break end
      r[#r + 1] = { s - 1, y - 1, e - s + 1 }
      x = e + 1
    end
  end
  return r
end

local SPRITES = { awake = runs(FROG_AWAKE), asleep = runs(FROG_ASLEEP), zzz = runs(ZZZ),
                  dizzyA = runs(FROG_DIZZY_A), dizzyB = runs(FROG_DIZZY_B), sweat = runs(SWEAT),
                  pad = runs(LILY_PAD), bolt = runs(BOLT) }

local function draw(sprite, x, y, flags)
  for _, r in ipairs(SPRITES[sprite]) do
    lcd.drawFilledRectangle(x + r[1], y + r[2], r[3], 1, flags)
  end
end

local function clamp(v, lo, hi)
  if v < lo then return lo elseif v > hi then return hi end
  return v
end

local function blinkOn()
  return (getTime() % 100) < 50          -- 1 Hz, getTime() is in 10 ms ticks
end

-- link quality: a wedge, narrow at the bottom and wide at the top, split down the middle
local LQ_AXIS, LQ_TOP, LQ_BOT, LQ_HW = 8, 1, 50, 7
local function linkWedge(tq, rq, warn)
  local rows = LQ_BOT - LQ_TOP
  local tqRows = math.floor(rows * clamp(tq, 0, 100) / 100 + 0.5)
  local rqRows = math.floor(rows * clamp(rq, 0, 100) / 100 + 0.5)
  local hide = (math.min(tq, rq) < warn) and not blinkOn()
  for y = LQ_TOP, LQ_BOT do
    local hw = 1 + math.floor((LQ_HW - 1) * (LQ_BOT - y) / rows + 0.5)
    lcd.drawPoint(LQ_AXIS - hw, y, FORCE)
    lcd.drawPoint(LQ_AXIS + hw, y, FORCE)
    local fromBottom = LQ_BOT - y
    if not hide and hw > 1 then
      if fromBottom < tqRows then lcd.drawFilledRectangle(LQ_AXIS - hw + 1, y, hw - 1, 1, FORCE) end
      if fromBottom < rqRows then lcd.drawFilledRectangle(LQ_AXIS + 1, y, hw - 1, 1, FORCE) end
    end
  end
  lcd.drawFilledRectangle(LQ_AXIS - LQ_HW, LQ_TOP, 2 * LQ_HW + 1, 1, FORCE)
end

-- radio battery: small horizontal cell, % and clock next to it
local function pocket()
  local s = getGeneralSettings()
  local v = getValue("tx-voltage")
  local pct = clamp(math.floor((v - s.battMin) * 100 / (s.battMax - s.battMin) + 0.5), 0, 100)
  local low = v < s.battWarn
  lcd.drawRectangle(0, 56, 18, 8, FORCE)
  lcd.drawFilledRectangle(18, 58, 2, 4, FORCE)
  if not (low and not blinkOn()) then
    local w = math.floor(14 * pct / 100 + 0.5)
    if w > 0 then lcd.drawFilledRectangle(2, 58, w, 4, FORCE) end
  end
  lcd.drawText(23, 57, string.format("%d%%", pct), SMLSIZE + (low and (INVERS + BLINK) or 0))
  local t = getDateTime()
  lcd.drawText(lcd.getLastRightPos() + 5, 57, string.format("%02d:%02d", t.hour, t.min), SMLSIZE)
end

-- drone battery: LAVA 1S pack standing up, connector housing and plug on top
local BX, BY, BW, BH = 105, 28, 15, 36
local function droneBattery(pct, low)
  lcd.drawFilledRectangle(BX + 5, BY - 9, 5, 3, FORCE)          -- plug
  lcd.drawFilledRectangle(BX - 1, BY - 6, BW + 2, 6, FORCE)     -- connector housing
  lcd.drawRectangle(BX, BY, BW, BH, FORCE)
  if pct ~= nil and not (low and not blinkOn()) then
    local h = math.floor((BH - 4) * pct / 100 + 0.5)
    if h > 0 then lcd.drawFilledRectangle(BX + 2, BY + BH - 2 - h, BW - 4, h, FORCE) end
  end
  draw("bolt", BX + 5, BY + 14, 0)                              -- XOR: shows on fill and on empty
end

local function percent(pct, low)
  if pct == nil then
    lcd.drawText(127, 1, "--", DBLSIZE + RIGHT)
    return
  end
  local flags = low and (INVERS + BLINK) or 0
  lcd.drawText(127, 10, "%", SMLSIZE + RIGHT + flags)
  lcd.drawText(lcd.getLastLeftPos() - 1, 1, string.format("%d", pct), DBLSIZE + RIGHT + flags)
end

-- Betaflight sends the mode name, plus "*" (ready to arm) or "!" (arming blocked) while disarmed
local function parseMode(fm)
  if fm == "!FS!" then return "!FS!", true, false, true end
  local last = string.sub(fm, -1)
  if last == "*" or last == "!" then
    local name = string.sub(fm, 1, -2)
    return MODES[name] or name, false, last == "!", false
  end
  return MODES[fm] or fm, true, false, false
end

local FX, FY = 46, 4                -- frog position
local function frogAndMode(linked, alarm)
  local fm = linked and getValue("FM") or 0
  local name, armed, blocked, failsafe = "NO LINK", false, false, false
  if type(fm) == "string" then name, armed, blocked, failsafe = parseMode(fm) end

  draw("pad", FX - 7, FY + 21, FORCE)
  if alarm and linked then                    -- failsafe, low battery, link critical: dizzy frog
    draw((math.floor(getTime() / 25) % 2 == 0) and "dizzyA" or "dizzyB", FX, FY, FORCE)
    draw("sweat", FX - 7, FY + 7, FORCE)
  elseif armed then
    draw("awake", FX, FY, FORCE)
  else
    draw("asleep", FX, FY, FORCE)
    if linked then draw("zzz", FX + 27, FY - 4, FORCE) end
  end

  local x, y, w, h = 36, 34, 47, 16
  local cx = x + math.floor(w / 2)
  local font = (name == "NO LINK") and SMLSIZE or MIDSIZE
  local ty = (font == SMLSIZE) and (y + 5) or (y + 2)
  if armed and not (failsafe and not blinkOn()) then
    lcd.drawFilledRectangle(x, y, w, h, FORCE)
    lcd.drawText(cx, ty, name, font + CENTER + INVERS)
  else
    if blocked then                                         -- dotted box: arming blocked
      for i = 0, w - 1, 2 do lcd.drawPoint(x + i, y, FORCE); lcd.drawPoint(x + i, y + h - 1, FORCE) end
      for j = 0, h - 1, 2 do lcd.drawPoint(x, y + j, FORCE); lcd.drawPoint(x + w - 1, y + j, FORCE) end
    else
      lcd.drawRectangle(x, y, w, h, FORCE)
    end
    lcd.drawText(cx, ty, name, font + CENTER)
  end
end

-- Vibration for the dizzy-frog situations:
--   low drone voltage -> L01/SF1 in the model (RxBt < 3.6 V, repeats every 10 s)
--   link critical     -> EdgeTX's own "RF signal critical" alarm (RQly < 42, vibrates with haptic mode "no keys")
--   failsafe          -> here: FM is a text sensor, which logical switches cannot compare.
-- EdgeTX calls background() while this screen is not shown; run() calls it while it is.
local lastBuzz = -1000
local function background()
  if getRSSI() > 0 and getValue("FM") == "!FS!" then
    local t = getTime()
    if t - lastBuzz >= 200 then           -- double buzz every 2 s
      playHaptic(40, 20)
      playHaptic(40, 0)
      lastBuzz = t
    end
  end
end

local function run(event)
  background()
  lcd.clear()
  local rq, rqWarn, rqCrit = getRSSI()  -- RQly for ELRS/CRSF, 0 when no telemetry
  local linked = rq > 0
  linkWedge(linked and getValue("TQly") or 0, rq, rqWarn)

  local pct, low = nil, false
  if linked then
    pct = clamp(getValue("Bat%"), 0, 100)
    local v = getValue("RxBt")
    low = v > 0 and v < DRONE_LOW_V
  end
  droneBattery(pct, low)
  percent(pct, low)
  local failsafe = linked and getValue("FM") == "!FS!"
  frogAndMode(linked, failsafe or low or (linked and rq < rqCrit))
  pocket()
  return 0
end

return { run = run, background = background }
