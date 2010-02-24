#-*-coding:utf-8-*-

import web
from forms import commentForm
from datetime import datetime
from settings import db, render, pageCount
from cache import mcache
from functions import *
import time
import hashlib
import markdown

d = dict()
d['pageCount'] = pageCount

def getCategories():
    return list(db.query(
            'SELECT * FROM categories ORDER BY name ASC'))

def getTags():
    return list(db.query(
            'SELECT * FROM tags ORDER BY name ASC'))

def getLinks():
    return list(db.query(
            'SELECT * FROM links ORDER BY name ASC'))

def my_loadhook():
    d['categories'] = getCategories()
    d['tags'] = getTags()
    d['links'] = getLinks()
    d['startTime'] = time.time()

class captcha:
    def GET(self):
        web.header("Content-Type", "image/gif")
        captcha = getCaptcha()
        web.config._session.captcha = captcha[0]
        return captcha[1].read()

class index(object):
    def GET(self):
        # 读取当前页的文章
        i = web.input(page=1)
        entryCount = db.query(
            'SELECT COUNT(id) AS num FROM entries')
        p = getPagination(i.page, entryCount[0].num, pageCount)
        entries = list(db.query(
            "SELECT en.id AS entryId, en.title AS title, "
            "en.content AS content, en.slug AS entry_slug, "
            "en.createdTime AS createdTime, "
            "en.commentNum AS commentNum, ca.id AS categoryId, "
            "ca.slug AS category_slug, ca.name AS category_name "
            "FROM entries en "
            "LEFT JOIN categories ca ON en.categoryId = ca.id "
            "ORDER BY createdTime DESC LIMIT $start, $limit",
            vars = {'start':(p[0] - 1) * pageCount, 'limit':pageCount}))
        for entry in entries:
            entry.tags = db.query(
                "SELECT * FROM entry_tag et "
                "LEFT JOIN tags t ON t.id = et.tagId "
                "WHERE et.entryId = $id", vars = {'id':entry.entryId})
            entry.content = markdown.markdown(entry.content)

        d['entries'] = entries
        d['p'] = p
        d['usedTime'] = time.time() - d['startTime']

        return render.index(**d)

class entry(object):
    def getEntry(self, slug):
        entry = list(db.query(
            'SELECT en.id AS entryId, en.title AS title, '
            'en.content AS content, en.slug AS entry_slug, '
            'en.createdTime AS createdTime, en.viewNum As viewNum, '
            'en.commentNum AS commentNum, ca.id AS categoryId, '
            'ca.slug AS category_slug, ca.name AS category_name '
            'FROM entries en '
            'LEFT JOIN categories ca ON en.categoryId = ca.id '
            'WHERE en.slug = $slug', vars={'slug':slug}))
        if len(entry) > 0:
            entry[0].content = markdown.markdown(entry[0].content)
            i= web.input(page = 1)
            comment = list(db.query(
                'SELECT COUNT(id) AS num FROM comments WHERE entryId = $id',
                vars = {'id':int(entry[0].entryId)}))
            p = getPagination(i.page, comment[0].num, pageCount)
            for one in entry:
                one.tags = list(db.query(
                    'SELECT * FROM entry_tag et '
                    'LEFT JOIN tags t ON t.id = et.tagId '
                    'WHERE et.entryId = $id',
                    vars = {'id': one.entryId}))
                one.comments = list(db.query(
                    'SELECT * FROM comments '
                    'WHERE entryId = $id '
                    'ORDER BY createdTime ASC LIMIT $start, $limit',
                    vars = {'id': one.entryId, 'start':(p[0] - 1) * pageCount,
                        'limit':pageCount}))
            return entry[0], p
        else:
            return None, None

    def GET(self, slug):
        f = commentForm()
        d['entry'], d['p'] = self.getEntry(slug)
        if d['entry']:
            db.update('entries',
                where='id=%s' % d['entry'].entryId,
                viewNum=int(d['entry'].viewNum)+1)
            d['f'] = f
            d['usedTime'] = time.time() - d['startTime']
            return render.entry(**d)

    def POST(self, slug):
        f = commentForm()
        d['entry'], d['p'] = self.getEntry(slug)
        if f.validates():
            db.insert('comments',
                    createdTime=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    entryId=d['entry'].entryId,
                    username=f.username.value,
                    email=f.email.value,
                    url=f.url.value,
                    comment=f.comment.value)
            db.update('entries',
                    where="id=%s" % d['entry'].entryId,
                    commentNum=int(d['entry'].commentNum)+1)
            raise web.seeother('/entry/%s/' % slug)
        else:
            d['f'] = f
            d['usedTime'] = time.time() - d['startTime']
            return render.entry(**d)

class page(object):
    def GET(self, slug):
        page = list(db.select('pages',
            where='slug = "%s"' % slug))
        if page:
            d['usedTime'] = time.time() - d['startTime']
            d['page'] = page[0]
            return render.page(**d)

class category(object):
    def GET(self, slug):
        category = list(db.query(
            'SELECT name FROM categories WHERE slug = $slug',
            vars = {'slug':slug}))
        if len(category) == 0:
            raise web.notfound()
        # 读取当前页的文章
        i = web.input(page=1)
        entryCount = db.query(
                'SELECT COUNT(en.id) AS num FROM entries en '
                'LEFT JOIN categories ca ON ca.id = en.categoryId '
                'WHERE ca.slug = $slug', vars = {'slug':slug})
        p = getPagination(i.page, entryCount[0].num, pageCount)
        entries = list(db.query(
            'SELECT en.id AS entryId, en.title AS title, en.content AS content, '
            'en.slug AS entry_slug, en.createdTime AS createdTime, '
            'ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name '
            'FROM entries en '
            'LEFT JOIN categories ca ON ca.id = en.categoryId '
            'WHERE ca.slug = $slug '
            'ORDER BY en.createdTime DESC LIMIT $start, $limit',
            vars = {'slug':slug, 'start':(p[0] - 1) * pageCount,
                'limit':pageCount}))
        d['entries'] = entries
        d['p'] = p
        d['usedTime'] = time.time() - d['startTime']
        d['category_name'] = category[0].name

        return render.category(**d)

class tag(object):
    def GET(self, slug):

        tag = db.query(
                'SELECT et.entryId AS id FROM entry_tag et '
                'LEFT JOIN tags t ON et.tagId = t.id '
                'WHERE t.name = $slug', vars = {'slug':slug})
        entry_list = [str(i.id) for i in tag]

        # 读取当前页的文章
        i = web.input(page=1)
        entryCount = len(entry_list)
        p = getPagination(i.page, entryCount, pageCount)
        entries = list(db.query(
            'SELECT en.id AS entryId, en.title AS title, '
            'en.content AS content, en.slug AS entry_slug, '
            'en.createdTime AS createdTime '
            'FROM entries en WHERE en.id in ($ids)',
            vars = {'ids':','.join(entry_list)}))

        d['entries'] = entries
        d['p'] = p
        d['usedTime'] = time.time() - d['startTime']
        d['slug'] = slug

        return render.tag(**d)

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
