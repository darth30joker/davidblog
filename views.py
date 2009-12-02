#coding:utf-8

import web
from davidblog import render

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
