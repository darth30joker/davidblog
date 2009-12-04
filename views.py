#coding:utf-8

import web
from davidblog import render
from forms import commentForm
from datetime import datetime

db = web.database(dbn = 'mysql', db = 'davidblog', user='root', pw = 'root')

class index(object):
    def GET(self):
        # 读取当前页的文章
        page = web.input(page=1)
        page = int(page.page)
        entry_count = db.query("SELECT COUNT(id) AS num FROM entries")
        pages = float(entry_count[0]['num'] / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        entries = list(db.query("SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON en.categoryId = ca.id ORDER BY createdTime DESC LIMIT $start, 10", vars = {'start':(page - 1) * 10}))
        for entry in entries:
            entry.tags = db.query("SELECT * FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId WHERE et.entryId = $id", vars = {'id':entry.entryId})

        #读取文章分类列表
        categories = db.query('SELECT * FROM categories ORDER BY name ASC')
        #读取tag列表
        tags = db.query('SELECT * FROM tags ORDER BY name ASC')
        #读取link列表
        links = db.query('SELECT * FROM links ORDER BY name ASC')
        return render.index(entries = entries, page = page, pages = pages, categories = categories, tags = tags, links = links)

class entry(object):
    def GET(self, slug):
        entry = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON en.categoryId = ca.id WHERE en.slug = $slug', vars={'slug':slug}))
        for one in entry:
            one.tags = db.query('SELECT * FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId WHERE et.entryId = $id', vars = {'id': one.entryId})
            one.comments = db.query('SELECT * FROM comments WHERE entryId = $id ORDER BY createdTime DESC', vars = {'id': one.entryId})

        #读取文章分类列表
        categories = db.query('SELECT * FROM categories ORDER BY name ASC')
        #读取tag列表
        tags = db.query('SELECT * FROM tags ORDER BY name ASC')
        #读取link列表
        links = db.query('SELECT * FROM links ORDER BY name ASC')

        f = commentForm()

        return render.entry(entry = entry[0], categories = categories, tags = tags, links = links, f = f)

class addComment(object):
    def POST(self):
        datas = web.input()
        createdTime = datetime.now().strftime("%Y-%m-%d %H:%M")
        if datas.url =="":
            datas.url = "#"
        db.insert('comments', entryId = datas.id, username = datas.username, email = datas.email, url = datas.url, createdTime = createdTime, comment = datas.comment)
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

        entries = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON ca.id = en.categoryId WHERE ca.slug = $slug ORDER BY en.createdTime DESC LIMIT $start, 10', vars = {'slug':slug, 'start':(page - 1) * 10}))

        #读取文章分类列表
        categories = db.query('SELECT * FROM categories ORDER BY name ASC')
        #读取tag列表
        tags = db.query('SELECT * FROM tags ORDER BY name ASC')
        #读取link列表
        links = db.query('SELECT * FROM links ORDER BY name ASC')

        return render.category(entries = entries, categories = categories, tags = tags, links = links, page = page, pages = pages)

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

        #读取文章分类列表
        categories = db.query('SELECT * FROM categories ORDER BY name ASC')
        #读取tag列表
        tags = db.query('SELECT * FROM tags ORDER BY name ASC')
        #读取link列表
        links = db.query('SELECT * FROM links ORDER BY name ASC')

        return render.tag(entries = entries, categories = categories, tags = tags, links = links, page = page, pages = pages)
