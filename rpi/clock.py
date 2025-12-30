import random
from datetime import datetime
from glob import glob

import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFont

from framebuffer import Framebuffer

# red & blue are 8 bits, green only 2??

font_sm = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size=140
)
font_big = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size=140
)


def display(fb, img):
    r = np.array(list(img.getdata(band=0)), dtype="uint8")
    g = np.array(list(img.getdata(band=1)), dtype="uint8") // 4
    b = np.array(list(img.getdata(band=2)), dtype="uint8")

    img_r = Image.fromarray(r.reshape(fb.size[1], fb.size[0]), mode=None)
    img_g = Image.fromarray(g.reshape(fb.size[1], fb.size[0]), mode=None)
    img_b = Image.fromarray(b.reshape(fb.size[1], fb.size[0]), mode=None)

    fb.show(
        Image.merge(
            "RGB", (img_r, img_g, img_b)
        )  # .transpose(PIL.Image.FLIP_LEFT_RIGHT)
    )


if __name__ == "__main__":
    fb = Framebuffer(0)
    images = sorted(glob("/home/butthead/images/*.jpg"))
    fname = random.choice(images)
    print(f"displaying {fname}")
    img = Image.open(fname).resize(fb.size)
    draw = ImageDraw.Draw(img)
    time = f"{datetime.now():%I:%M %p}"
    outer_size = font_big.getsize(time)
    inner_size = font_sm.getsize(time)
    outer_loc = (fb.size[0] - outer_size[0]) // 2, (fb.size[1] - outer_size[1]) // 2
    outer_2 = 6 + (fb.size[0] - outer_size[0]) // 2, (fb.size[1] - outer_size[1]) // 2
    inner_loc = 3 + (fb.size[0] - inner_size[0]) // 2, (fb.size[1] - inner_size[1]) // 2
    draw.text(outer_loc, time, fill="black", font=font_big)
    draw.text(outer_2, time, fill="black", font=font_big)
    draw.text(inner_loc, time, fill="white", font=font_sm)
    display(fb, img)
