# author Red
# RedGarph — 生成应用图标资源

"""将批准的图标稿处理为 PNG 和多尺寸 ICO。"""

from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


ROOT = Path(__file__).resolve().parent.parent
OUT_PNG = ROOT / "resources" / "icon.png"
OUT_ICO = ROOT / "resources" / "icon.ico"
SIZES = [16, 24, 32, 48, 64, 128, 256]


def _remove_preview_background(image: Image.Image) -> Image.Image:
    """去除生成稿外围的黑色预览底，保留图标本体和圆角透明区。"""
    image = image.convert("RGBA")
    rgb = image.convert("RGB")

    # 生成稿的预览底接近纯黑，而图标底座是明显更亮的石墨色。
    # 仅移除与预览底相连的低亮度边缘，避免误伤图标内部的深色区域。
    background = Image.new("L", rgb.size)
    pixels = (
        rgb.get_flattened_data()
        if hasattr(rgb, "get_flattened_data")
        else rgb.getdata()
    )
    background.putdata([
        0 if max(r, g, b) <= 8 else 255
        for r, g, b in pixels
    ])
    alpha = ImageChops.multiply(image.getchannel("A"), background)
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
    image.putalpha(alpha)

    bbox = alpha.getbbox()
    if not bbox:
        raise ValueError("图标稿为空，无法生成应用图标")

    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    padding = max(8, int(max(width, height) * 0.025))
    side = max(width, height) + padding * 2
    center_x = (bbox[0] + bbox[2]) / 2
    center_y = (bbox[1] + bbox[3]) / 2
    left = int(round(center_x - side / 2))
    top = int(round(center_y - side / 2))

    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    source_box = (
        max(0, left),
        max(0, top),
        min(image.width, left + side),
        min(image.height, top + side),
    )
    piece = image.crop(source_box)
    canvas.alpha_composite(piece, (source_box[0] - left, source_box[1] - top))
    return canvas


def main():
    if not OUT_PNG.exists():
        raise FileNotFoundError(f"找不到图标稿: {OUT_PNG}")

    icon = _remove_preview_background(Image.open(OUT_PNG))
    rendered = icon.resize((256, 256), Image.Resampling.LANCZOS)
    rendered.save(OUT_PNG, "PNG", optimize=True)
    print(f"PNG -> {OUT_PNG}")

    icon.save(OUT_ICO, "ICO", sizes=[(size, size) for size in SIZES])
    print(f"ICO -> {OUT_ICO} ({', '.join(f'{size}px' for size in SIZES)})")


if __name__ == "__main__":
    main()
