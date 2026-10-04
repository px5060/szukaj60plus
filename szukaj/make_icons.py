"""Ikony SZUKAJ+ (odróżnialne od RAZEM i SZUKAJ): fioletowe tło, lupa, napis 50+/60+.  Uruchom: python3 make_icons.py 50+"""
import sys, pathlib
from PIL import Image, ImageDraw, ImageFont
lbl = sys.argv[1]; out = pathlib.Path(__file__).resolve().parent.parent
for size in (192, 512):
    s = size / 512
    im = Image.new('RGB', (size, size), '#7030a0'); d = ImageDraw.Draw(im)
    d.ellipse([110*s, 70*s, 330*s, 290*s], outline='white', width=int(34*s))
    d.line([300*s, 262*s, 410*s, 372*s], fill='white', width=int(46*s))
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', int(110*s))
    d.text((256*s, 440*s), lbl, font=f, fill='white', anchor='mm')
    im.save(out / f'szukaj-{size}.png')
print('ikony zapisane', out)
