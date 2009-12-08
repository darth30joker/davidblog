#coding:utf-8

import web
from forms import commentForm
from datetime import datetime
from settings import db, render, pageCount
from cache import mcache

def getCategories():
    categories = mcache.get('categories')
    if categories is None:
        categories = list(db.query('SELECT * FROM categories ORDER BY name ASC'))
        mcache.set('categories', categories)
    return categories

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

class index(object):
    def GET(self):
        # 读取当前页的文章
        page = web.input(page=1)
        page = int(page.page)
        entry_count = db.query("SELECT COUNT(id) AS num FROM entries")
        pages = float(entry_count[0]['num'] / pageCount)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        entries = list(db.query("SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, en.commentNum AS commentNum, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON en.categoryId = ca.id ORDER BY createdTime DESC LIMIT $start, $limit", vars = {'start':(page - 1) * pageCount, 'limit':pageCount}))
        for entry in entries:
            entry.tags = db.query("SELECT * FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId WHERE et.entryId = $id", vars = {'id':entry.entryId})

        return render.index(entries = entries, page = page, pages = pages, categories = getCategories(), tags = getTags(), links = getLinks())

class entry(object):
    def GET(self, slug):
        entry = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, en.commentNum AS commentNum, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON en.categoryId = ca.id WHERE en.slug = $slug', vars={'slug':slug}))
        page = web.input(page=1)
        page = int(page.page)
        comment_count = db.query("SELECT COUNT(id) AS num FROM comments WHERE entryId = %s" % entry[0].id)
        pages = float(entry_count[0]['num'] / pageCount)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        for one in entry:
            one.tags = db.query('SELECT * FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId WHERE et.entryId = $id', vars = {'id': one.entryId})
            one.comments = db.query('SELECT * FROM comments WHERE entryId = $id ORDER BY createdTime DESC LIMIT $start, $limit', vars = {'id': one.entryId, 'start':(page - 1) * pageCount, 'limit':pageCount})

        f = commentForm()

        return render.entry(entry = entry[0], categories = getCategories(), tags = getTags(), links = getLinks(), f = f)

class addComment(object):
    def POST(self):
        datas = web.input()
        createdTime = datetime.now().strftime("%Y-%m-%d %H:%M")
        if datas.url =="":
            datas.url = "#"
        db.insert('comments', entryId = datas.id, username = datas.username, email = datas.email, url = datas.url, createdTime = createdTime, comment = datas.comment)
        entry = db.query('SELECT commentNum FROM entries WHERE id = $id', vars = {'id':datas.id})
        db.update('entries', where = 'id = %s' % datas.id, commentNum = entry[0].commentNum + 1)
        return render.comment(datas = datas, createdTime = createdTime)

class category(object):
    def GET(self, slug):
        # 读取当前页的文章
        page = web.input(page=1)
        page = int(page.page)
        entry_count = db.query("SELECT COUNT(en.id) AS num FROM entries en LEFT JOIN categories ca ON ca.id = en.categoryId WHERE ca.slug = $slug", vars = {'slug':slug})
        pages = float(entry_count[0]['num'] / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages

        entries = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON ca.id = en.categoryId WHERE ca.slug = $slug ORDER BY en.createdTime DESC LIMIT $start, $limit', vars = {'slug':slug, 'start':(page - 1) * pageCount, 'limit':pageCount}))

        return render.category(entries = entries, categories = getCategories(), tags = getTags(), links = getLinks(), page = page, pages = pages)

class tag(object):
    def GET(self, slug):

        tag = db.query('SELECT et.entryId AS id FROM entry_tag et LEFT JOIN tags t ON et.tagId = t.id WHERE t.name = $slug', vars = {'slug':slug})
        entry_list = [str(i.id) for i in tag]

        # 读取当前页的文章
        page = web.input(page=1)
        page = int(page.page)
        entry_count = len(entry_list)
        pages = float(entry_count / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages

        entries = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime FROM entries en WHERE en.id in ($ids)', vars = {'ids':','.join(entry_list)}))

        return render.tag(entries = entries, categories = getCategories(), tags = getTags(), links = getLinks(), page = page, pages = pages)

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
