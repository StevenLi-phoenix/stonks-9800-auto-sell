"""
只移光标、不点击。把光标依次放到 8 行的位置上，截屏并把光标真实位置标在图上。
让我们看到 SetCursorPos 是否真的把光标放到了我们以为的地方。
"""
import ctypes
import ctypes.wintypes
import time

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

from PIL import ImageGrab, ImageDraw

_user32 = ctypes.windll.user32
MONITOR_OFFSET = (-1920, 0)


def move(virt):
    _user32.SetCursorPos(int(virt[0]), int(virt[1]))


def cursor():
    pt = ctypes.wintypes.POINT()
    _user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)


def grab_with_cursor(path, label):
    img = ImageGrab.grab(all_screens=True)
    game = img.crop((0, 0, 1920, 1080)).copy()
    cx, cy = cursor()
    # 拼接图原点 = (-1920, 0)，所以游戏内坐标 = 虚拟坐标 - (-1920, 0)
    img_x = cx - MONITOR_OFFSET[0]
    img_y = cy - MONITOR_OFFSET[1]
    d = ImageDraw.Draw(game)
    d.line([(img_x - 30, img_y), (img_x + 30, img_y)], fill="lime", width=4)
    d.line([(img_x, img_y - 30), (img_x, img_y + 30)], fill="lime", width=4)
    d.ellipse([(img_x - 8, img_y - 8), (img_x + 8, img_y + 8)],
              outline="lime", width=3)
    d.text((img_x + 35, img_y - 35),
           f"{label}\nvirt=({cx},{cy})\ngame=({img_x},{img_y})",
           fill="lime")
    game.save(path)
    return (cx, cy), (img_x, img_y)


def main():
    # 测试目标 (游戏内坐标)
    targets = [
        ("name_col_row0", (200, 245)),
        ("name_col_row1", (200, 303)),
        ("center_row0", (500, 245)),
        ("price_row0", (950, 245)),
        ("page_arrow", (985, 885)),
        ("close_btn", (1755, 130)),
    ]
    for label, (gx, gy) in targets:
        virt = (gx + MONITOR_OFFSET[0], gy + MONITOR_OFFSET[1])
        move(virt)
        time.sleep(0.3)
        actual_virt, actual_img = grab_with_cursor(f"hover_{label}.png", label)
        match = "OK" if actual_virt == virt else "MISS"
        print(f"{match} {label}: 期望 game({gx},{gy})/virt{virt}  "
              f"实际 game{actual_img}/virt{actual_virt}")


if __name__ == "__main__":
    main()
