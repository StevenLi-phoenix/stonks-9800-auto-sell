"""
定位验证工具:把脚本要点的位置标记在游戏截屏上,生成 locate_preview.png。
不会真的点击,只是看看坐标对不对。

用法:
    python locate.py
"""

from PIL import ImageGrab, ImageDraw, ImageFont

import auto_sell as cfg  # 复用同一份坐标常量


# 副屏在虚拟桌面里的位置 (左上角)
# 多屏 ImageGrab 拼接后的本地坐标 = 虚拟桌面坐标 - 拼接图原点
# all_screens 模式下,拼接图原点 = 最左/上屏的左上角 = (-1920, 0)
# 所以 "虚拟桌面坐标" 减去 (-1920, 0) 就是图内坐标。
GRAB_ORIGIN = (-1920, 0)


def to_image_xy(virtual_xy):
    return (virtual_xy[0] - GRAB_ORIGIN[0], virtual_xy[1] - GRAB_ORIGIN[1])


def draw_cross(draw, xy, label, color="red"):
    x, y = xy
    r = 18
    draw.line([(x - r, y), (x + r, y)], fill=color, width=3)
    draw.line([(x, y - r), (x, y + r)], fill=color, width=3)
    draw.ellipse([(x - 6, y - 6), (x + 6, y + 6)], outline=color, width=2)
    draw.text((x + r + 4, y - r), label, fill=color)


def main():
    img = ImageGrab.grab(all_screens=True)
    print(f"全屏拼接尺寸: {img.size}  (拼接原点假设 = {GRAB_ORIGIN})")

    # 只裁出副屏 (游戏所在) — 即左侧 1920x1080
    game = img.crop((0, 0, 1920, 1080))
    draw = ImageDraw.Draw(game)

    targets = []
    # 11 行的位置
    for i in range(cfg.ROWS_PER_PAGE):
        virt = cfg.abs_xy(
            (cfg.FIRST_ROW_XY[0], cfg.FIRST_ROW_XY[1] + i * cfg.ROW_HEIGHT)
        )
        targets.append((virt, f"row{i}"))

    targets += [
        (cfg.abs_xy(cfg.SELL_BUTTON_XY), "SELL"),
        (cfg.abs_xy(cfg.CONFIRM_BUTTON_XY), "CONFIRM"),
        (cfg.abs_xy(cfg.NEXT_PAGE_XY), "NEXT_PAGE"),
        (cfg.abs_xy(cfg.CLOSE_BUTTON_XY), "CLOSE"),
    ]

    for virt_xy, label in targets:
        img_xy = to_image_xy(virt_xy)
        print(f"{label:10s} 虚拟桌面={virt_xy}  图内={img_xy}")
        draw_cross(draw, img_xy, label)

    out = r"D:\Documents\PythonProjects\locate_preview.png"
    game.save(out)
    print(f"已保存: {out}")


if __name__ == "__main__":
    main()
