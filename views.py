#coding:utf-8

import web
from forms import commentForm
from datetime import datetime
from settings import db, render, pageCount
from cache import mcache
import time
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from utils import Pagination

d = dict()

def getTags():
    tags = mcache.get('tags')
    if tags is None:
        tags = list(db.query('SELECT * FROM tags ORDER BY name ASC'))
        mcache.set('tags', tags)
    return tags

def getLinks():
    links = mcache.get('links')
    if links is None:
        links = list(db.query('SELECT * FROM links ORDER BY name ASC'))
        mcache.set('links', links)
    return links

def my_loadhook():
    d['tags'] = getTags()
    d['links'] = getLinks()
    d['startTime'] = time.time()
    global session
    session = web.config._session
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))

def my_handler(handler):
    d['tags'] = getTags()
    d['links'] = getLinks()
    d['startTime'] = time.time()
    web.ctx.session = web.config._session
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()

class index(object):
    def GET(self):
        # 读取当前页的文章
        i = web.input(page=1)
        entryCount = web.ctx.orm.query(Entry).count()
        p = Pagination(entryCount, 5, int(i.page))

        d['entries'] = web.ctx.orm.query(Entry).order_by(Entry.createdTime)[p.get_start():p.limit]
        d['p'] = p
        d['usedTime'] = time.time() - d['startTime']

        return render.index(**d)

class entry(object):
    def GET(self, slug):
        entry = web.ctx.orm.query(Entry).filter_by(slug=slug).first()
        i = web.input(page = 1)
        commentCount = web.ctx.orm.query(Comment).filter_by(entryId=entry.id).count()
        p = Pagination(commentCount, 5, int(i.page))
        comments = web.ctx.orm.query(Comment).filter_by(entryId=entry.id)[p.get_start():p.limit]
        f = commentForm()

        d['p'] = p
        d['entry'] = entry
        d['f'] = f
        d['usedTime'] = time.time() - d['startTime']

        return render.entry(**d)

class page(object):
    def GET(self, slug):
        page = list(db.select('pages', where='slug = "%s"' % slug))
        if not page:
            datas['usedTime'] = time.time() - datas['startTime']
            return render.page(**datas)

class tag(object):
    def GET(self, slug):

        tag = db.query('SELECT et.entryId AS id FROM entry_tag et LEFT JOIN tags t ON et.tagId = t.id WHERE t.name = $slug', vars = {'slug':slug})
        entry_list = [str(i.id) for i in tag]

        # 读取当前页的文章
        page = web.input(page=1)
        page = int(page.page)
        entry_count = len(entry_list)
        pages = float(float(entry_count) / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages

        entries = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime FROM entries en WHERE en.id in ($ids)', vars = {'ids':','.join(entry_list)}))

        datas['entries'] = entries
        datas['page'] = page
        datas['pages'] = pages
        datas['usedTime'] = time.time() - datas['startTime']
        datas['slug'] = slug

        return render.tag(**datas)

class rss(object):
    def GET(self):
        entries = list(db.query('SELECT * FROM entries ORDER BY createdTime DESC LIMIT 10'))
        rss = '<?xml version="1.0" encoding="utf-8" ?>\n'
        rss = rss + '<rss version="2.0">\n'
        rss = rss + '<channel>\n'
        rss = rss + '<title>' + u'泥泞的沼泽' + '</title>\n'
        rss = rss + '<link>http://davidshieh.cn/</link>\n'
        rss = rss + '<description>' + u'泥泞的沼泽' + '</description>\n'
        rss = rss + '<lastBuildDate>' + datetime.now().strftime('%a, %d %b  %Y %H:%M:%S GMT') + '</lastBuildDate>\n'
        rss = rss + '<language>zh-cn</language>\n'
        for one in entries:
            rss = rss + '<item>\n'
            rss = rss + '<title>' + one.title + '</title>\n'
            rss = rss + '<link>http://davidshieh.cn/entry/' + one.slug + '</link>\n'
            rss = rss + '<guid>http://davidshieh.cn/entry/' + one.slug + '</link>\n'
            rss = rss + '<pubDate>' + one.createdTime.strftime('%a, %d %b  %Y %H:%M:%S GMT') + '</pubDate>\n'
            rss = rss + '<description>' + one.content[:100] + '</description>\n'
            rss = rss + '</item>\n'

        rss = rss + '</channel>\n'
        rss = rss + '</rss>\n'
        web.header('Content-Type', 'text/xml')
        rss = rss.encode('utf-8')
        return rss

def notfound():
    return web.notfound("对不起, 您所访问的地址并不存在.")

def internalerror():
    return web.internalerror("对不起, 网站遇到一个不可遇见的错误.")

class test(object):
    def GET(self):
        """
        if session:
            return session.captcha
        else:
            return 'there'
        """
        return web.ctx.session
