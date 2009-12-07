#coding:utf-8

import web
from forms import categoryForm
from datetime import datetime
from settings import db
from settings import render_admin as render 
from cache import mcache

class index(object):
    def GET(self):
        entryNum = db.query('SELECT COUNT(id) AS num FROM entries')
        commentNum = db.query('SELECT COUNT(id) AS num FROM comments')
        categoryNum = db.query('SELECT COUNT(id) AS num FROM categories')
        tagNum = db.query('SELECT COUNT(id) AS num FROM tags')
        linkNum = db.query('SELECT COUNT(id) AS num FROM links')
        return render.index(
                entryNum = entryNum[0].num,
                commentNum = commentNum[0].num,
                categoryNum = categoryNum[0].num,
                tagNum = tagNum[0].num,
                linkNum = linkNum[0].num
            )

class categories(object):
    def GET(self):
        page = web.input(page=1)
        page = int(page.page)
        categoryNum = db.query("SELECT COUNT(id) AS num FROM categories")
        pages = float(categoryNum[0]['num'] / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        categories = list(db.query('SELECT * FROM categories ORDER BY name ASC LIMIT $start, 10', vars={'start': (page - 1) * 10}))

        return render.category(categories = categories, page = page, pages = pages)

class category_add(object):
    def GET(self):
        f = categoryForm()
        return render.category_add(f = f)

    def POST(self):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('categories', name = data['name'], slug = data['slug'])
        return web.seeother('/categories/')

class category_edit(object):
    def GET(self, id):
        f = categoryForm()
        category = list(db.query("SELECT * FROM categories WHERE id = $id", vars = {'id':id}))
        f.get('name').value = category[0].name
        f.get('slug').value = category[0].slug
        return render.category_edit(f = f, id = category[0].id)

    def POST(self, id):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.update('categories', where = "id = %s" % id, name = data['name'], slug = data['slug'])
        return web.seeother('/categories/')

class category_del(object):
    def GET(self, id):
        db.delete('categories', where = 'id = %s' % id)
        return web.seeother('/categories/')

class tags(object):
    def GET(self):
        page = web.input(page=1)
        page = int(page.page)
        categoryNum = db.query("SELECT COUNT(id) AS num FROM tags")
        pages = float(categoryNum[0]['num'] / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        categories = list(db.query('SELECT * FROM tags ORDER BY name ASC LIMIT $start, 10', vars={'start': (page - 1) * 10}))

        return render.tag(categories = categories, page = page, pages = pages)

class tag_add(object):
    def GET(self):
        f = categoryForm()
        return render.tag_add(f = f)

    def POST(self):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('tags', name = data['name'], slug = data['slug'])
        return web.seeother('/tags/')

class tag_edit(object):
    def GET(self, id):
        f = categoryForm()
        tag = list(db.query("SELECT * FROM tags WHERE id = $id", vars = {'id':id}))
        f.get('name').value = tag[0].name
        f.get('slug').value = tag[0].slug
        return render.tag_edit(f = f, id = tag[0].id)

    def POST(self, id):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.update('tags', where = "id = %s" % id, name = data['name'], slug = data['slug'])
        return web.seeother('/tags/')

class tag_del(object):
    def GET(self, id):
        db.delete('tags', where = 'id = %s' % id)
        return web.seeother('/tags/')

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

        entries = list(db.query('SELECT en.id AS entryId, en.title AS title, en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime, ca.id AS categoryId, ca.slug AS category_slug, ca.name AS category_name FROM entries en LEFT JOIN categories ca ON ca.id = en.categoryId WHERE ca.slug = $slug ORDER BY en.createdTime DESC LIMIT $start, 10', vars = {'slug':slug, 'start':(page - 1) * 10}))

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

class reblog(object):
    def GET(self):
        raise web.seeother('/')
