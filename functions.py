#-*-coding:utf-8-*-

import web
import Image, ImageDraw, ImageFont, cStringIO, random

__all__ = [
        'getPagination', 'getCaptcha'
    ]

def getPagination(page, total, itemPerPage):
    page = int(page)
    total = int(total)
    itemPerPage = int(itemPerPage)
    floatPages = float(total) / itemPerPage
    pages = total / itemPerPage
    if pages == 0:
        pages = 1
    if floatPages > pages:
        pages = pages + 1
    if page < 1:
        page = 1
    if page > pages:
        page = pages
    return (page, pages)

def getCaptcha():
    """
    Generate a captcha image
    """
    im = Image.new("RGB", (85, 35))
    draw = ImageDraw.Draw(im)
    for x in range(0, 100):
        for y in range(0, 60):
            draw.point((x, y), (135, 191, 107))
    font = ImageFont.truetype('FreeMono.ttf', 25)
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    word = ''
    for i in range(5):
        word = word + alphabet[random.randint(0, len(alphabet) -1)]
    draw.text((5, 5), word, font=font, fill=(0, 0, 0))
    f = cStringIO.StringIO()
    im.save(f, "GIF")
    f.seek(0)
    return word, f

