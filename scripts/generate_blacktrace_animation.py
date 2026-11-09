
from pathlib import Path
import math

from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------
# BLACKTRACE ANIMATION GENERATOR
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "blacktrace" / "motion" / "blacktrace-investigation.gif"

WIDTH = 960
HEIGHT = 320

FRAME_COUNT = 40
FRAME_DURATION = 100

# BLACKTRACE visual system
VOID = (8, 9, 13)
PANEL = (17, 20, 27)
CRIMSON = (239, 51, 74)
BLOOD = (103, 19, 31)
ALERT = (255, 82, 99)
PAPER = (241, 243, 245)
MUTED = (146, 153, 165)
GREEN = (56, 217, 150)
GOLD = (214, 179, 106)

# Windows font paths
FONT_REGULAR = Path("C:/Windows/Fonts/consola.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/consolab.ttf")

def load_font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()

FONT_SMALL = load_font(FONT_REGULAR, 12)
FONT_MEDIUM = load_font(FONT_REGULAR, 16)
FONT_BOLD = load_font(FONT_BOLD, 27)
FONT_TITLE = load_font(FONT_BOLD, 34)

def draw_background(draw):
    draw.rectangle(
        (0, 0, WIDTH, HEIGHT),
        fill=VOID
    )

    # Subtle technical grid
    for x in range(0, WIDTH, 32):
        draw.line(
            (x, 0, x, HEIGHT),
            fill=(18, 20, 27),
            width=1
        )

    for y in range(0, HEIGHT, 32):
        draw.line(
            (0, y, WIDTH, y),
            fill=(18, 20, 27),
            width=1
        )

def draw_frame(frame_index):
    image = Image.new("RGB", (WIDTH, HEIGHT), VOID)
    draw = ImageDraw.Draw(image)

    draw_background(draw)

    # Outer classified frame
    draw.rectangle(
        (14, 14, WIDTH - 14, HEIGHT - 14),
        outline=BLOOD,
        width=2
    )

    # Corner brackets
    corners = [
        (14, 14, 65, 14),
        (14, 14, 14, 48),
        (WIDTH - 65, 14, WIDTH - 14, 14),
        (WIDTH - 14, 14, WIDTH - 14, 48),
        (14, HEIGHT - 48, 14, HEIGHT - 14),
        (14, HEIGHT - 14, 65, HEIGHT - 14),
        (WIDTH - 65, HEIGHT - 14, WIDTH - 14, HEIGHT - 14),
        (WIDTH - 14, HEIGHT - 48, WIDTH - 14, HEIGHT - 14),
    ]

    for line in corners:
        draw.line(line, fill=CRIMSON, width=4)

    # Header strip
    draw.rectangle(
        (30, 30, WIDTH - 30, 65),
        fill=(39, 16, 23)
    )

    draw.text(
        (48, 40),
        "BLACKTRACE // INVESTIGATION UNIT",
        font=FONT_MEDIUM,
        fill=CRIMSON
    )

    draw.text(
        (WIDTH - 185, 42),
        "SYSTEM ACTIVE",
        font=FONT_SMALL,
        fill=GREEN
    )

    # Main title
    draw.text(
        (48, 88),
        "INVESTIGATION",
        font=FONT_TITLE,
        fill=PAPER
    )

    draw.text(
        (50, 135),
        "DIGITAL FOOTPRINT // CASE 001",
        font=FONT_SMALL,
        fill=MUTED
    )

    # Surveillance viewport
    viewport = (48, 180, 650, 270)

    draw.rounded_rectangle(
        viewport,
        radius=4,
        fill=PANEL,
        outline=BLOOD,
        width=2
    )

    # Scan movement
    scan_x = 58 + (frame_index / (FRAME_COUNT - 1)) * 580

    draw.line(
        (scan_x, 187, scan_x, 263),
        fill=CRIMSON,
        width=2
    )

    # Subtle scan glow
    draw.line(
        (scan_x - 5, 187, scan_x - 5, 263),
        fill=(75, 24, 35),
        width=2
    )

    # Target lock animation
    pulse = 18 + 4 * math.sin(
        2 * math.pi * frame_index / FRAME_COUNT
    )

    cx, cy = 350, 225

    draw.ellipse(
        (
            cx - pulse,
            cy - pulse,
            cx + pulse,
            cy + pulse
        ),
        outline=ALERT,
        width=2
    )

    draw.ellipse(
        (cx - 3, cy - 3, cx + 3, cy + 3),
        fill=CRIMSON
    )

    draw.line(
        (cx - 34, cy, cx - 24, cy),
        fill=CRIMSON,
        width=1
    )

    draw.line(
        (cx + 24, cy, cx + 34, cy),
        fill=CRIMSON,
        width=1
    )

    draw.line(
        (cx, cy - 34, cx, cy - 24),
        fill=CRIMSON,
        width=1
    )

    draw.line(
        (cx, cy + 24, cx, cy + 34),
        fill=CRIMSON,
        width=1
    )

    # Evidence status panel
    draw.rounded_rectangle(
        (680, 180, 912, 270),
        radius=4,
        fill=PANEL,
        outline=BLOOD,
        width=2
    )

    draw.text(
        (698, 195),
        "EVIDENCE STATUS",
        font=FONT_SMALL,
        fill=CRIMSON
    )

    # Four-step progress sequence
    active_step = min(
        3,
        frame_index // 10
    )

    steps = [
        "SYSTEM BOOT",
        "SCANNING",
        "EVIDENCE FOUND",
        "TARGET LOCKED"
    ]

    for index, label in enumerate(steps):
        y = 218 + index * 12

        color = GREEN if index <= active_step else MUTED

        draw.text(
            (698, y),
            label,
            font=load_font(FONT_REGULAR, 9),
            fill=color
        )

        if index <= active_step:
            draw.ellipse(
                (885, y + 2, 891, y + 8),
                fill=GREEN
            )

    # Footer
    draw.line(
        (48, 287, WIDTH - 48, 287),
        fill=BLOOD,
        width=1
    )

    draw.text(
        (48, 295),
        "CLASSIFICATION // RESTRICTED",
        font=FONT_SMALL,
        fill=MUTED
    )

    draw.text(
        (WIDTH - 210, 295),
        "BT-005 // LIVE TRACE",
        font=FONT_SMALL,
        fill=CRIMSON
    )

    return image

def main():
    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    frames = [
        draw_frame(index)
        for index in range(FRAME_COUNT)
    ]

    # GIF uses a shared palette for consistent rendering.
    first_frame = frames[0].convert(
        "P",
        palette=Image.Palette.ADAPTIVE,
        colors=128
    )

    converted_frames = [
        first_frame
    ]

    for frame in frames[1:]:
        converted_frames.append(
            frame.quantize(
                palette=first_frame,
                dither=Image.Dither.NONE
            )
        )

    first_frame.save(
        OUTPUT,
        save_all=True,
        append_images=converted_frames[1:],
        duration=FRAME_DURATION,
        loop=0,
        optimize=True,
        disposal=2
    )

    print("BLACKTRACE ANIMATION GENERATED")
    print(f"Output: {OUTPUT}")
    print(f"Frames: {FRAME_COUNT}")
    print(f"Dimensions: {WIDTH} x {HEIGHT}")
    print(f"Duration: {FRAME_COUNT * FRAME_DURATION / 1000:.1f} seconds")
    print(f"File size: {OUTPUT.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()
