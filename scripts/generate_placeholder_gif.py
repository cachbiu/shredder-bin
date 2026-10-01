"""Generate a looping placeholder shredder GIF into assets/."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets" / "shredder.gif"
SIZE = 160
FRAMES = 12


def _frame(step: int) -> Image.Image:
    img = Image.new("RGB", (SIZE, SIZE), (26, 29, 34))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((28, 70, 132, 138), radius=10, fill=(70, 78, 88), outline=(30, 36, 48), width=3)
    y = 20 + (step * 8) % 56
    draw.rectangle((52, y, 108, y + 28), fill=(245, 245, 240), outline=(180, 180, 170))
    for i in range(6):
        x = 36 + i * 16
        draw.ellipse((x, 86, x + 12, 102), fill=(40, 40, 44))
    draw.rectangle((32, 118, 128, 134), fill=(45, 48, 54))
    shred_y = 102 + (step % 4)
    for i in range(8):
        sx = 40 + i * 10
        draw.line((sx, shred_y, sx + 2, 136), fill=(220, 220, 210), width=2)
    return img


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [_frame(i) for i in range(FRAMES)]
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=80,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
