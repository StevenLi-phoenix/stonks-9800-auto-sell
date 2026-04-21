"""STONKS-9800 自动卖出 — 从最后一页往前卖,保留前 N 页。"""
import argparse
import ctypes
import ctypes.wintypes
import time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

from PIL import ImageGrab           # noqa: E402
import pydirectinput                # noqa: E402

pydirectinput.FAILSAFE = True
pydirectinput.PAUSE = 0

_user32 = ctypes.windll.user32
MONITOR_OFFSET = (-1920, 0)

# 已验证坐标
FIRST_ROW_XY    = (200, 245)
SELL_BUTTON_XY  = (1250, 835)
CONFIRM_YES_XY  = (800, 660)
PAGE_PREV_XY    = (835, 885)
PAGE_NEXT_XY    = (985, 885)

# 顶部 tab (住宅/商业/地域) — 估算
TAB_XY = {
    "residential": (370, 130),   # 住宅
    "commercial":  (725, 130),   # 商业
    "regional":    (1080, 130),  # 地域
}

CLICK_HOLD       = 0.12
DELAY_AFTER_ROW  = 0.55
DELAY_AFTER_SELL = 0.55
DELAY_AFTER_YES  = 0.85
DELAY_PAGE       = 0.10


def click_game(g, hold=CLICK_HOLD):
    _user32.SetCursorPos(int(g[0] + MONITOR_OFFSET[0]),
                         int(g[1] + MONITOR_OFFSET[1]))
    time.sleep(0.18)
    pydirectinput.mouseDown()
    time.sleep(hold)
    pydirectinput.mouseUp()


def press_esc():
    pydirectinput.press("escape")


def to_last_page(n: int = 80):
    """疯狂点 ▶ 直到无效,确保到最后一页。"""
    for _ in range(n):
        click_game(PAGE_NEXT_XY, hold=0.04)
        time.sleep(DELAY_PAGE)


def sell_one():
    click_game(FIRST_ROW_XY); time.sleep(DELAY_AFTER_ROW)
    click_game(SELL_BUTTON_XY); time.sleep(DELAY_AFTER_SELL)
    click_game(CONFIRM_YES_XY); time.sleep(DELAY_AFTER_YES)


def first_row_brightness():
    img = ImageGrab.grab(all_screens=True).crop((0, 0, 1920, 1080))
    s = n = 0
    for x in range(160, 210, 5):
        for y in range(235, 260, 5):
            r, g, b = img.getpixel((x, y))
            s += r + g + b; n += 1
    return s / n


def run(count: int, refresh_every: int):
    print("3 秒后开始,Ctrl+C 或鼠标到主屏 (0,0) 停止。")
    time.sleep(3)

    # 0. 关闭可能开着的对话框
    print("ESC 关闭对话框…")
    press_esc(); time.sleep(0.3)
    press_esc(); time.sleep(0.3)

    # 1. 翻到最后一页
    print("翻到最后一页…")
    to_last_page(80)
    time.sleep(0.5)

    sold = 0
    empty_streak = 0
    for i in range(count):
        bright = first_row_brightness()
        if bright > 600:           # 列表为空
            empty_streak += 1
            print(f"[{i+1}] 第一行亮度={bright:.0f} 像是空,连续 {empty_streak} 次")
            if empty_streak >= 3:
                print("看似全部卖光,提前结束。")
                break
            time.sleep(0.5)
            continue
        empty_streak = 0
        print(f"[{i+1}/{count}] 卖出 (亮度={bright:.0f})")
        sell_one()
        sold += 1

        # 周期性回刷:点 ▶ 几次确保仍在最后一页(防止卖空当前页后跳前)
        if refresh_every > 0 and (sold % refresh_every == 0):
            for _ in range(5):
                click_game(PAGE_NEXT_XY, hold=0.04)
                time.sleep(DELAY_PAGE)

    print(f"完成: 卖出 {sold} 个。")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--count", type=int, default=572,
                   help="最多卖多少个 (默认 572 = 52页 * 11)")
    p.add_argument("--refresh-every", type=int, default=11,
                   help="每卖 N 个就再点几次 ▶ 确保在最后一页 (0=不刷)")
    a = p.parse_args()
    run(count=a.count, refresh_every=a.refresh_every)
