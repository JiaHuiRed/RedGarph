#author Red
#260620 Red&小宋 RedGarph — 生成 macOS 风格应用图标

"""生成 RedGarph 应用图标（256x256, 多种尺寸 .ico + .png）"""

from PIL import Image, ImageDraw
from pathlib import Path

SIZE = 512
OUT = Path(__file__).resolve().parent.parent / "resources" / "icon.png"
OUT_ICO = Path(__file__).resolve().parent.parent / "resources" / "icon.ico"

def rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius, fill=fill)

def draw_icon():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── macOS 圆角矩形底座 ──
    margin = 24
    r = 80
    box = (margin, margin, SIZE - margin, SIZE - margin)

    # 渐变底色（手工分段，暖红→橙）
    steps = 60
    for i in range(steps):
        t = i / steps
        y0 = box[1] + (box[3] - box[1]) * t
        y1 = box[1] + (box[3] - box[1]) * (t + 1 / steps)
        r2 = int(220 - t * 60)
        g2 = int(80 + t * 100)
        b2 = int(50 + t * 30)
        strip = (box[0], y0, box[2], y1)
        draw.rounded_rectangle(
            strip, r,
            fill=(r2, g2, b2, 255) if i < steps - 1 else (r2, g2, b2, 0),
        )

    # 重新画完整圆角矩形基底（纯色填充，上面叠渐变效果更好）
    # 改用纯渐变色背景：画两个半圆角矩形叠加
    img2 = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)

    # 从上到下渐变：深红→暖橙
    for y in range(box[1], box[3]):
        t = (y - box[1]) / (box[3] - box[1])
        rr = int(210 - t * 30)       # 210→180
        gg = int(70 + t * 100)       # 70→170
        bb = int(40 + t * 50)        # 40→90
        draw2.line([(box[0], y), (box[2], y)], fill=(rr, gg, bb))

    # 用圆角矩形 mask 裁剪
    mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(box, r, fill=255)
    img = Image.composite(img2, img, mask)

    # ── 重新获取 draw（基于新 img） ──
    draw = ImageDraw.Draw(img)

    # ── 图形内容：取景框 + 风景剪影 ──
    cx, cy = SIZE // 2, SIZE // 2

    # 太阳（右上）
    sun_r = 55
    sx = cx + 110
    sy = cy - 60
    draw.ellipse([sx - sun_r, sy - sun_r, sx + sun_r, sy + sun_r],
                 fill=(255, 220, 80, 255))

    # 太阳光晕
    for i in range(3):
        glow_r = sun_r + 20 + i * 25
        glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([sx - glow_r, sy - glow_r, sx + glow_r, sy + glow_r],
                      fill=(255, 220, 80, 40 - i * 10))
        img.alpha_composite(glow)

    # 远山（背景，浅色）
    mountain_color = (100, 60, 50, 180)
    peaks = [
        (60, 310, 180, 180),    # 左峰
        (180, 340, 280, 200),   # 中左
        (280, 300, 420, 160),   # 中峰（最高）
        (400, 320, 500, 190),   # 右峰
    ]
    for x0, y_base, x1, y_peak in peaks:
        points = [(x0, y_base), ((x0 + x1) // 2, y_peak), (x1, y_base)]
        draw.polygon(points, fill=mountain_color)

    # 近山（前景，深色）
    mountain_color2 = (70, 40, 35, 220)
    peaks2 = [
        (30, 380, 160, 220),
        (150, 400, 300, 240),
        (290, 390, 440, 200),
        (420, 400, 510, 250),
    ]
    for x0, y_base, x1, y_peak in peaks2:
        points = [(x0, y_base), ((x0 + x1) // 2, y_peak), (x1, y_base)]
        draw.polygon(points, fill=mountain_color2)

    # 雪顶（中峰）
    snow_pts = [
        (280, 300), (350, 165), (420, 300),
        (390, 210), (350, 175), (310, 215),
    ]
    draw.polygon(snow_pts[:4], fill=(255, 255, 255, 200))
    draw.polygon(snow_pts[2:], fill=(255, 255, 255, 180))

    # 前景地面
    draw.rectangle([box[0] + 10, 390, box[2] - 10, box[3] - 10],
                   fill=(45, 30, 25, 230))

    # 取景框（半透明边框）
    frame_margin = 30
    frame_draw = ImageDraw.Draw(img)
    # 四角 L 形标记（摄影取景框风格）
    l = 35
    gap = 12
    corners = [
        (box[0] + gap, box[1] + gap, box[0] + gap + l, box[1] + gap),         # 左上横
        (box[0] + gap, box[1] + gap, box[0] + gap, box[1] + gap + l),         # 左上竖
        (box[2] - gap - l, box[1] + gap, box[2] - gap, box[1] + gap),         # 右上横
        (box[2] - gap, box[1] + gap, box[2] - gap, box[1] + gap + l),         # 右上竖
        (box[0] + gap, box[3] - gap, box[0] + gap + l, box[3] - gap),         # 左下横
        (box[0] + gap, box[3] - gap - l, box[0] + gap, box[3] - gap),         # 左下竖
        (box[2] - gap - l, box[3] - gap, box[2] - gap, box[3] - gap),         # 右下横
        (box[2] - gap, box[3] - gap - l, box[2] - gap, box[3] - gap),         # 右下竖
    ]
    for x0, y0, x1, y1 in corners:
        draw.line([(x0, y0), (x1, y1)], fill=(255, 255, 255, 100), width=4)

    return img

def main():
    img = draw_icon()
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # 保存 PNG
    img.resize((256, 256), Image.LANCZOS).save(OUT, "PNG")
    print(f"PNG -> {OUT}")

    # 生成 .ico（包含多尺寸）
    sizes = [16, 32, 48, 64, 128, 256]
    imgs = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    imgs[0].save(OUT_ICO, "ICO", sizes=[(s, s) for s in sizes], append_images=imgs[1:])
    print(f"ICO -> {OUT_ICO}")

if __name__ == "__main__":
    main()
