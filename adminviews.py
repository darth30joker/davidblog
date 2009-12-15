#coding:utf-8

import web
from forms import categoryForm
from datetime import datetime
from settings import db, pageCount
from settings import render_admin as render 
from cache import mcache

para = dict()
para['pageCount'] = pageCount

def getCategories():
    categories = mcache.get('adminCategories')
    if categories is None:
        categories = list(db.query("SELECT * FROM categories ORDER BY name ASC"))
        mcache.set('adminCategories', categories)
    return categories

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

class entry(object):
    def GET(self):
        page = web.input(page=1)
        page = int(page.page)
        entryNum = db.query("SELECT COUNT(id) AS num FROM entries")
        pages = float(float(entryNum[0]['num']) / pageCount)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        entries = list(db.query('SELECT e.id AS entryId, e.title AS title, e.slug AS slug, c.name AS categoryName FROM entries e LEFT JOIN categories c ON c.id = e.categoryId ORDER BY e.createdTime DESC LIMIT $start, $limit', vars={'start': (page - 1) * pageCount, 'limit':pageCount}))

        para['page'] = page
        para['pages'] = pages
        para['entries'] = entries

        return render.entry(**para)

class entry_add(object):
    def GET(self):
        para['categories'] = getCategories()
        return render.entry_add(**para)

    def POST(self):
        data = web.input(tags = None)
        entryId = db.insert('entries', title = data['title'], slug = data['slug'], categoryId = data['categoryId'], createdTime = datetime.now(), modifiedTime = datetime.now(), content = data['content'])
        if data['tags'] is not None:
            tags = [i.lstrip().rstrip() for i in data['tags'].split(',')]
            for tag in tags:
                temp = list(db.query("SELECT * FROM tags WHERE name = $name", vars={'name':tag}))
                if len(temp) > 0:
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)', vars={'entryId':entryId, 'tagId':temp[0].id})
                    db.query('UPDATE tags SET entryNum = $entryNum WHERE tagId = $tagId', vars={'entryNum':int(temp[0].entryNum) + 1, 'tagId':temp[0].id})
                else:
                    tagId = db.query("INSERT INTO tags (`name`) VALUES ('%s')" % tag.replace("'", "''"))
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)', vars={'entryId':entryId, 'tagId':tagId})
        return web.seeother('/entry/')

class entry_edit(object):
    def GET(self, id):
        entry = list(db.query("SELECT e.id AS entryId, e.title AS title, e.slug AS slug, e.categoryId AS categoryId, e.content AS content, c.name AS categoryName FROM entries e LEFT JOIN categories c ON c.id = e.categoryId WHERE e.id = $id", vars={'id':id}))
        tags = list(db.query("SELECT t.name AS name FROM entry_tag et LEFT JOIN tags t ON et.tagId = t.id WHERE et.entryId = $id", vars={'id':id}))
        if len(tags) > 0:
            entry[0].tagList = ",".join([one.name for one in tags])
        else:
            entry[0].tagList = ''
        para['entry'] = entry[0]
        para['categories'] = getCategories()
        return render.entry_edit(**para)

    def POST(self, id):
        entry = list(db.query("SELECT * FROM entries WHERE id = $id", vars={'id':id}))
        entryTags = list(db.query("SELECT t.name AS name FROM entry_tag et LEFT JOIN tags t ON et.tagId = t.id WHERE et.entryId = $id", vars={'id':id}))
        entryTags = [one.name for one in entryTags]

        data = web.input(title=None, slug=None, categoryId=None, tags=None, content=None)
        #处理tags, 这个比较麻烦
        #首先要读出来该文章原先的tags, 再跟更改后的tags比较
        #如果有tag被删除, 则需要将entry_tag中的记录删掉
        #删tag的时候, 如果tag的entryNum等于0, 则把改记录删除, 否则把entryNum-1
        #添加tag的时候, 先判断tag是否存在, 如果tag存在, 则将entry和tag绑定, 并将tag的entryNum+1, 否则创建tag
        if data.tags is not None:
            tagList = data.tags.split(',')
            originalTags = set(entryTags)
            newTags = set(tagList)
            tagsAdd = newTags - originalTags
            tagsDel = originalTags - newTags
            #添加tag
            for tag in tagsAdd:
                temp = list(db.query("SELECT * FROM tags WHERE name = $name", vars={'name':tag}))
                if len(temp) > 0:
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)', vars={'entryId':entry[0].id, 'tagId':temp[0].id})
                    db.query('UPDATE tags SET entryNum = $entryNum WHERE tagId = $tagId', vars={'entryNum':int(temp[0].entryNum) + 1, 'tagId':temp[0].id})
                else:
                    tagId = db.insert('tags', name = tag.replace("'", "''"))
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)', vars={'entryId':entry[0].id, 'tagId':tagId})
            #删除tag
            for tag in tagsDel:
                temp = list(db.query("SELECT * FROM tags WHERE name = $name", vars={'name':tag}))
                if len(temp) > 0:
                    if temp[0].entryNum == 1:
                        db.query('DELETE FROM tags WHERE id = $tagId', vars={'tagId':temp[0].id})
                    else:
                        db.query('UPDATE tags SET `entryNum` = $entryNum WHERE id = $tagId', vars={'entryNum':int(temp[0].entryNum) - 1, 'tagId':temp[0].id})
                    db.query('DELETE FROM entry_tag WHERE entryId = $entryId AND tagId = $tagId', vars={'entryId':entry[0].id, 'tagId':temp[0].id})

        return web.seeother('/entry/')

class entry_del(object):
    def GET(self, id):
        entry = list(db.query('SELECT * FROM entries WHERE id = $id', vars={'id':id}))
        if len(entry) > 0:
            db.query('DELETE FROM entries WHERE id = $id', vars={'id':id})
            category = list(db.query('SELECT * FROM categories WHERE id = $id', vars={'id':entry[0].categoryId}))
            db.query('UPDATE categories SET `entryNum` = $entryNum WHERE id = $categoryId', vars={'entryNum':int(category[0].entryNum) - 1, 'categoryId':category[0].id})
            tags = list(db.query('SELECT t.id AS tagId, t.entryNum AS entryNum FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId WHERE et.entryId = $entryId', vars= {'entryId':entry[0].id}))
            for tag in tags:
                if tag.entryNum > 2:
                    db.query('UPDATE tags SET `entryNum` = $entryNum WHERE id = $id', vars={'entryNum':int(tag.entryNum) - 1, 'id':tag.tagId})
                if temp[0].entryNum == 1:
                    db.query('DELETE FROM tags WHERE id = $tagId', vars={'tagId':tag.tagId})
                db.query('DELETE FROM entry_tag WHERE entryId = $entryId AND tagId = $tagId', vars={'entryId':tag.entryId, 'tagId':tag.tagId})
        return web.seeother('/entry/')

class links(object):
    def GET(self):
        page = web.input(page=1)
        page = int(page.page)
        linkNum = list(db.query("SELECT COUNT(id) AS num FROM links"))
        pages = float(linkNum[0]['num'] / 10)
        if pages > int(pages):
            pages = int(pages + 1)
        elif pages == 0:
            pages = 1
        else:
            pages = int(pages)
        if page > pages:
            page = pages
        links = list(db.query('SELECT * FROM links ORDER BY name ASC LIMIT $start, 10', vars={'start': (page - 1) * 10}))

        para['page'] = page
        para['pages'] = pages
        para['links'] = links

        return render.tag(**para)

class link_add(object):
    def GET(self):
        f = linkForm()

        para['f'] = f

        return render.link_add(**para)

    def POST(self):
        f = linkForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('links', name = data['name'], url = data['url'])
        return web.seeother('/links/')

class link_edit(object):
    def GET(self, id):
        f = linkForm()
        links = list(db.query("SELECT * FROM links WHERE id = $id", vars = {'id':id}))
        f.get('name').value = links[0].name
        f.get('url').value = links[0].slug

        para['f'] = f

        return render.link_edit(**para)

    def POST(self, id):
        f = linkForm()
        if f.validates():
            data = dict(**f.d)
            db.update('links', where = "id = %s" % id, name = data['name'], url = data['url'])
        return web.seeother('/links/')

class link_del(object):
    def GET(self, id):
        db.delete('links', where = 'id = %s' % id)
        return web.seeother('/links/')

class reblog(object):
    def GET(self):
        raise web.seeother('/')
