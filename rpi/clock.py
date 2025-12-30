from datetime import datetime
import random
import mmap
import sys
import os
import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from glob import glob


FB_DEV = "/dev/fb0"

with open(f"/sys/class/graphics/{os.path.basename(FB_DEV)}/virtual_size", "r") as f:
    width_str, height_str = f.read().strip().split(",")
    WIDTH, HEIGHT = int(width_str), int(height_str)

with open(f"/sys/class/graphics/{os.path.basename(FB_DEV)}/bits_per_pixel", "r") as f:
    BPP = int(f.read().strip())

BYTES_PER_PIX = BPP // 8


def write_pixel(fb, x, y, r, g, b, a):
    offset = y * WIDTH * BYTES_PER_PIX + x * BYTES_PER_PIX
    if BPP == 32:
        fb[offset] = b
        fb[offset + 1] = r
        fb[offset + 2] = g
        fb[offset + 3] = a
    elif BPP == 16:
        # 5 bits per color
        bytes = b >> 3
        bytes <<= 5
        bytes |= r >> 3
        bytes <<= 5
        bytes |= g >> 3
        bytes <<= 1
        fb[offset] = bytes >> 8
        fb[offset + 1] = bytes & 255


def test_img():
    with open(FB_DEV, "w+b") as fb_file:
        # Memory map the file to a byte array
        fb_memory = mmap.mmap(
            fb_file.fileno(),
            WIDTH * HEIGHT * BYTES_PER_PIX,
            mmap.MAP_SHARED,
            mmap.PROT_WRITE | mmap.PROT_READ,
        )
        for rgb in ([255, 0, 0], [0, 255, 0], [0, 0, 255]):
            for x in range(100, 200):
                for y in range(100, 200):
                    write_pixel(fb_memory, x, y, rgb[0], rgb[1], rgb[2], 0)


font_sm = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size=140
)
font_big = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size=140
)


def getsize(font, text):
    left, top, right, bottom = font.getbbox(text)
    return (right - left, bottom - top)


def blit_img(fname):
    img = Image.open(fname)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    if img.size[0] > WIDTH or img.size[1] > HEIGHT:
        raise Exception(
            f"image dimensions {r_chan.size} exceed screen ({WIDTH}, {HEIGHT})"
        )
    elif img.size[0] < WIDTH or img.size[1] < HEIGHT:
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(img)
    time = f"{datetime.now():%I:%M %p}"
    outer_size = getsize(font_big, time)
    inner_size = getsize(font_sm, time)
    outer_loc = (WIDTH - outer_size[0]) // 2, (HEIGHT - outer_size[1]) // 2
    outer_2 = 6 + (WIDTH - outer_size[0]) // 2, (HEIGHT - outer_size[1]) // 2
    inner_loc = 3 + (WIDTH - inner_size[0]) // 2, (HEIGHT - inner_size[1]) // 2
    draw.text(outer_loc, time, fill="black", font=font_big)
    draw.text(outer_2, time, fill="black", font=font_big)
    draw.text(inner_loc, time, fill="white", font=font_sm)

    if BPP == 32:
        fb = np.memmap(FB_DEV, dtype="uint8", mode="w+", shape=(HEIGHT, WIDTH, 4))
        fb[:] = np.asarray(img)

    elif BPP == 16:
        fb = np.memmap(FB_DEV, dtype="uint16", mode="w+", shape=(HEIGHT, WIDTH))
        arr = np.asarray(img, dtype=np.uint8)  # shape (H, W, 3)
        r = (arr[..., 0] >> 3).astype(np.uint16)
        g = (arr[..., 1] >> 2).astype(np.uint16)
        b = (arr[..., 2] >> 3).astype(np.uint16)
        rgb565 = (r << 11) | (g << 5) | b
        fb[:] = rgb565


if __name__ == "__main__":
    # test_img()
    blit_img(random.choice(glob("/home/butthead/clock_images/*.jpg")))
