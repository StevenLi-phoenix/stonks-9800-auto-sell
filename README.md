# STONKS-9800 Auto Sell

A one-shot Python script that auto-sells your real estate in
[STONKS-9800: Stock Market Simulator](https://store.steampowered.com/app/1539340/STONKS9800_Stock_Market_Simulator/)
(tested on Early Access ver. 0.9.0.11).

Click the asset list, click "Sell", confirm "Yes" — repeat until done.

> Built and tested on Windows 11 with the game running on a 1920×1080 secondary
> monitor (left) while the main monitor (2560×1600 @ 200% DPI) sat on the right.

## Why this exists

Liquidating hundreds of properties one by one is tedious. The game's UI gives
no bulk-sell option. So: 605 clicks become one command.

## Requirements

- Windows 10/11
- Python 3.8+
- `pip install pydirectinput pyautogui pillow`

## Usage

```powershell
# Default: 572 sells, periodically nudges back to last page
python auto_sell.py

# Sell up to 999 (auto-stops if list looks empty)
python auto_sell.py --count 999

# Don't nudge back to last page each cycle
python auto_sell.py --refresh-every 0
```

The script gives you a 3-second head start — bring the game window to the
front. To abort at any time: move the mouse to the **top-left corner of your
primary monitor** (pyautogui fail-safe) or hit `Ctrl+C` in the terminal.

## How it works (the interesting bits)

Three problems had to be solved before clicks would actually register:

1. **Mixed-DPI multi-monitor** — The script declares
   `PROCESS_PER_MONITOR_DPI_AWARE` so all coordinates are physical pixels and
   the secondary monitor (with negative X) is reachable.

2. **`SetCursorPos` for movement** — `pydirectinput.click(x, y)` can't address
   negative coordinates. We use Win32 `SetCursorPos` to move the cursor (which
   handles the virtual desktop correctly), then issue a click in place.

3. **Hold the button down** — A naive `click()` (down + immediate up) is
   ignored by the game. The fix is `mouseDown()` → `sleep(0.12s)` →
   `mouseUp()`. Apparently STONKS samples mouse state on a slow tick.

The flow per asset:

```
click row (200, 245)     -> "档案" detail dialog opens
click sell (1250, 835)   -> "are you sure?" confirm dialog
click yes (800, 660)     -> sold; list refreshes
```

A pixel-brightness probe at the first row's icon position serves as a
"list is empty" sentinel.

## Caveats

- All coordinates are hard-coded for a 1920×1080 game window at the
  exact position shown above. Different monitor layout or game version =
  re-calibrate. The repo includes `hover.py` and `locate.py` to help.
- The game can keep generating new listings while you sell, so "done" is
  more of a moving target than a hard stop. Set `--count` accordingly.
- This is a one-shot tool — written for a single afternoon's task. Use the
  scaffolding as a reference, not a production library.

## License

MIT — do whatever you want.
