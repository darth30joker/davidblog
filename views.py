#coding:utf-8
from datetime import datetime
import time
import cgi
import random
import web
from forms import commentForm
from settings import db, render, pageCount
from cache import mcache
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
from utils import Pagination, getCaptcha
from markdown import markdown
import templatefilters

d = dict()

def getTags():
    return web.ctx.orm.query(Tag).order_by('tags.name').all()

def getLinks():
    return web.ctx.orm.query(Link).order_by('links.name').all()

def my_loadhook():
    web.ctx.session = web.config._session
    d['startTime'] = time.time()

def my_handler(handler):
    web.ctx.orm = scoped_session(sessionmaker(bind=engine))
    d['tags'] = getTags()
    d['links'] = getLinks()
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

class captcha:
    def GET(self):
        web.header('Content-type', 'image/gif')
        captcha = getCaptcha()
        web.ctx.session.captcha = captcha[0]
        return captcha[1].read()

class index(object):
    def GET(self):
        # 读取当前页的文章
        i = web.input(page=1)
        ids = [int(one.id) for one in web.ctx.orm.query(Entry.id).all()]
        randomEntries = [web.ctx.orm.query(Entry).filter_by(id=id).first() for id in random.sample(ids, 5)]
        entryCount = web.ctx.orm.query(Entry).count()
        p = Pagination(entryCount, 5, int(i.page))
        d['entries'] = web.ctx.orm.query(Entry).order_by('entries.createdTime DESC')[p.start:p.start + p.limit]
        d['p'] = p
        d['usedTime'] = time.time() - d['startTime']
        d['randomEntries'] = randomEntries
        return render.index(**d)

class entry(object):
    def getEntry(self, slug):
        if slug:
            entry = web.ctx.orm.query(Entry).filter_by(slug=slug).first()
            i = web.input(page = 1)
            commentCount = web.ctx.orm.query(Comment).filter_by(entryId=entry.id).count()
            p = Pagination(int(commentCount), 5, int(i.page))
            entry.comments = web.ctx.orm.query(Comment).filter_by(entryId=entry.id)[p.start:p.limit]
            return (entry, p)

    def GET(self, slug):
        entry, p = self.getEntry(slug)
        entry.viewNum = entry.viewNum + 1
        f = commentForm()
        d['p'] = p
        d['entry'] = entry
        d['f'] = f
        d['usedTime'] = time.time() - d['startTime']
        return render.entry(**d)

    def POST(self, slug):
        entry, p = self.getEntry(slug)
        f = commentForm()
        if f.validates():
            comment = Comment(entry.id, f.username.value, f.email.value, f.url.value, f.comment.value)
            entry.commentNum = entry.commentNum + 1
            entry.viewNum = entry.viewNum - 1
            web.ctx.orm.add(comment)
            raise web.seeother('/entry/%s/' % slug)
        else:
            d['p'] = p
            d['entry'] = entry
            d['f'] = f
            d['usedTime'] = time.time() - d['startTime']
            return render.entry(**d)

class page(object):
    def GET(self, slug):
        page = web.ctx.orm.query(Page).filter_by(slug=slug).first()
        if page:
            d['usedTime'] = time.time() - d['startTime']
            d['page'] = page
            return render.page(**d)

class tag(object):
    def GET(self, slug):
        i = web.input(page=1)
        try:
            page = int(i.page)
        except:
            page = 1
        tag = web.ctx.orm.query(Tag).filter_by(name=slug).first()
        p = Pagination(len(tag.entries), 20, page)
        entries = tag.entries[::-1][p.start:p.limit]
        d['tag'] = tag
        d['p'] = p
        d['entries'] = entries
        d['usedTime'] = time.time() - d['startTime']
        return render.tag(**d)

class rss(object):
    def GET(self):
        entries = web.ctx.orm.query(Entry).order_by('entries.createdTime DESC').all()[:10]
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
            rss = rss + '<link>http://davidx.me/entry/' + one.slug + '</link>\n'
            rss = rss + '<guid>http://davidx.me/entry/' + one.slug + '</guid>\n'
            rss = rss + '<pubDate>' + one.createdTime.strftime('%a, %d %b  %Y %H:%M:%S GMT') + '</pubDate>\n'
            rss = rss + '<description>' + templatefilters.content(one.content) + '</description>\n'
            rss = rss + '</item>\n'

        rss = rss + '</channel>\n'
        rss = rss + '</rss>\n'
        #web.header('Content-Type', 'text/xml')
        rss = rss.encode('utf-8')
        return rss

def notfound():
    return web.notfound("对不起, 您所访问的地址并不存在.")

def internalerror():
    return web.internalerror("对不起, 网站遇到一个不可遇见的错误.")
