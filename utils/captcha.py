#-*-coding:utf-8-*-
import Image, ImageDraw, ImageFont, cStringIO, random

def getCaptcha():
    """
    Generate a captcha image
    """
    im = Image.new("RGB", (62, 26))
    draw = ImageDraw.Draw(im)
    for x in range(0, 100):
        for y in range(0, 60):
            draw.point((x, y), (135, 191, 107))
    font = ImageFont.truetype('FreeMono.ttf', 18)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    word = ''
    for i in range(5):
        word = word + alphabet[random.randint(0, len(alphabet) -1)]
    draw.text((3, 3), word, font=font, fill=(0, 0, 0))
    f = cStringIO.StringIO()
    im.save(f, "GIF")
    f.seek(0)
    return word, f
