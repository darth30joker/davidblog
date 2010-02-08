#-*-coding:utf-8-*-

import hashlib
import web
from forms import *
from datetime import datetime
from settings import db, pageCount
from settings import render_admin as render 
from cache import mcache

d = {}

def my_loadhook():
    global session
    session = web.config._session

def getCategories():
    return list(db.query("SELECT * FROM categories ORDER BY name ASC"))

def getPagination(page, total, itemPerPage):
    """
    page is current page,
    total is the total number of items,
    itemPerPage is the number of each page
    """
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

def login_required(func):
    def Function(*args):
        if session.isAdmin == 0:
            raise web.seeother('/login/')
        else:
            return func(*args)
    return Function

class back(object):
    def GET(self):
        raise web.seeother('/')

class index(object):
    @login_required
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

class login(object):
    def GET(self):
        return render.login(**d)

    def POST(self):
        i = web.input()
        if i.username and i.password:
            admins = list(db.query(
                    'SELECT * FROM admins WHERE username = "davidx"'
                ))
            if len(admins) > 0:
                if hashlib.md5(i.password).hexdigest() == admins[0].password:
                    session.isAdmin = 1
                    raise web.seeother('/')
        d['error'] = "Wrong username/password!"
        return render.login(**d)

class logout(object):
    def GET(self):
        session.kill()
        raise web.seeother('/')

class category_list(object):
    @login_required
    def GET(self):
        i = web.input(page=1)
        total = list(db.query("SELECT COUNT(id) AS num FROM categories"))[0]
        p = getPagination(i.page, total.num, pageCount)
        categories = list(db.query('SELECT * FROM categories '
            'ORDER BY name ASC LIMIT $start, $limit',
            vars={'start': (p[0] - 1) * pageCount, 'limit':pageCount}))
        d['p'] = p
        d['c'] = categories
        return render.category_list(**d)

class category_add(object):
    @login_required
    def GET(self):
        d['f'] = categoryForm()
        return render.category_add(**d)

    @login_required
    def POST(self):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('categories', name = data['name'], slug = data['slug'])
        return web.seeother('/categories/')

class category_edit(object):
    @login_required
    def GET(self, id):
        f = categoryForm()
        category = list(db.query("SELECT * FROM categories WHERE id = $id", vars = {'id':id}))
        f.get('name').value = category[0].name
        f.get('slug').value = category[0].slug
        return render.category_edit(f = f, id = category[0].id)

    @login_required
    def POST(self, id):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.update('categories', where = "id = %s" % id, name = data['name'], slug = data['slug'])
        return web.seeother('/categories/')

class category_del(object):
    @login_required
    def GET(self, id):
        db.delete('categories', where = 'id = %s' % id)
        return web.seeother('/categories/')

class tag_list(object):
    @login_required
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
        d['categories'] = list(db.query('SELECT * FROM tags ORDER BY name '
            'ASC LIMIT $start, 10', vars={'start': (page - 1) * 10}))
        return render.tag(**d)

class tag_add(object):
    @login_required
    def GET(self):
        f = categoryForm()
        return render.tag_add(f = f)

    @login_required
    def POST(self):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('tags', name = data['name'], slug = data['slug'])
        return web.seeother('/tags/')

class tag_edit(object):
    @login_required
    def GET(self, id):
        f = categoryForm()
        tag = list(db.query("SELECT * FROM tags WHERE id = $id", vars = {'id':id}))
        f.get('name').value = tag[0].name
        f.get('slug').value = tag[0].slug
        return render.tag_edit(f = f, id = tag[0].id)

    @login_required
    def POST(self, id):
        f = categoryForm()
        if f.validates():
            data = dict(**f.d)
            db.update('tags', where = "id = %s" % id, name = data['name'], slug = data['slug'])
        return web.seeother('/tags/')

class tag_del(object):
    @login_required
    def GET(self, id):
        db.delete('tags', where = 'id = %s' % id)
        return web.seeother('/tags/')

class category(object):
    @login_required
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
    @login_required
    def GET(self, slug):

        tag = db.query('SELECT et.entryId AS id FROM entry_tag et '
            'LEFT JOIN tags t ON et.tagId = t.id WHERE t.name = $slug',
            vars = {'slug':slug})
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

        d['entries'] = list(db.query('SELECT en.id AS entryId, en.title AS title, '
                'en.content AS content, en.slug AS entry_slug, en.createdTime AS createdTime '
                'FROM entries en WHERE en.id in ($ids)', vars = {'ids':','.join(entry_list)}))

        return render.tag(entries = entries, categories = getCategories(), tags = getTags(), links = getLinks(), page = page, pages = pages)

class entry_list(object):
    @login_required
    def GET(self):
        i = web.input(page=1)
        entryCount = db.query("SELECT COUNT(id) AS num FROM entries")
        p = getPagination(int(i.page), entryCount[0].num, 20)
        entries = list(db.query(
            'SELECT e.id AS entryId, e.title AS title, e.slug AS slug, '
            'c.name AS categoryName '
            'FROM entries e '
            'LEFT JOIN categories c ON c.id = e.categoryId '
            'ORDER BY e.createdTime DESC LIMIT $start, $limit',
            vars={'start': (p[0] - 1) * 20, 'limit':20}))
        d['p'] = p
        d['entries'] = entries
        return render.entry_list(**d)

class entry_add(object):
    @login_required
    def GET(self):
        d['categories'] = getCategories()
        return render.entry_add(**d)

    @login_required
    def POST(self):
        i = web.input(tags = None)
        entryId = db.insert('entries',
                title = i['title'],
                slug = i['slug'],
                categoryId = i['categoryId'],
                createdTime = datetime.now(),
                modifiedTime = datetime.now(),
                content = i['content'])
        category = list(db.select('categories', where='id = %s' % i['categoryId']))
        db.update('categories', where='id = %s' % i['categoryId'],
                entryNum = int(category[0].entryNum) + 1)
        if i.get('tags') is not None:
            tags = [i.lstrip().rstrip() for i in i['tags'].split(',')]
            for tag in tags:
                temp = list(db.query("SELECT * FROM tags WHERE name = $name",
                    vars={'name':tag}))
                if len(temp) > 0:
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)',
                            vars={'entryId':entryId, 'tagId':temp[0].id})
                    db.query('UPDATE tags SET entryNum = $entryNum WHERE tagId = $tagId',
                            vars={'entryNum':int(temp[0].entryNum) + 1, 'tagId':temp[0].id})
                else:
                    tagId = db.insert('tags', name = tag.replace("'", "''"), entryNum = 1)
                    db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)',
                            vars={'entryId':entryId, 'tagId':tagId})
        return web.seeother('/entry/')

class entry_edit(object):

    def getEntry(self, id):
        entry = list(db.query(
            'SELECT * FROM entries WHERE id = $id',
            vars={'id':int(id)}))
        if len(entry) > 0:
            entry = entry[0]
            entryTags = list(db.query(
                'SELECT t.name AS name '
                'FROM entry_tag et '
                'LEFT JOIN tags t ON et.tagId = t.id '
                'WHERE et.entryId = $id', vars={'id':int(id)}))
            entry.tags = ", ".join([one.name for one in entryTags])
            return entry
        else:
            return None

    @login_required
    def GET(self, id):
        entry = self.getEntry(id)
        if entry:
            f = entryForm()
            f.title.value = entry.title
            f.slug.value = entry.slug
            d['entry'] = entry
            d['categories'] = getCategories()
            d['f'] = f
            return render.entry_edit(**d)

    @login_required
    def POST(self, id):
        f = entryForm()
        entry = self.getEntry(id)
        i = web.input(title=None, slug=None, categoryId=None, tags=None, content=None)
        if f.validates():
            #处理tags, 这个比较麻烦
            #首先要读出来该文章原先的tags, 再跟更改后的tags比较
            #如果有tag被删除, 则需要将entry_tag中的记录删掉
            #删tag的时候, 如果tag的entryNum等于0, 则把改记录删除, 否则把entryNum-1
            #添加tag的时候, 先判断tag是否存在, 如果tag存在, 则将entry和tag绑定, 并将tag的entryNum+1, 否则创建tag
            if i.tags is not None:
                newTags = set([i.strip() for i in i.tags.split(',')])
                originalTags = set([i.strip() for i in entry.tags.split(',')])
                tagsAdd = list(newTags - originalTags)
                tagsDel = list(originalTags - newTags)
                #添加tag
                if tagsAdd:
                    for tag in tagsAdd:
                        temp = list(db.query("SELECT * FROM tags WHERE LOWER(name) = $name",
                            vars={'name':tag.lower()}))
                        if temp:
                            db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)',
                                    vars={'entryId':int(entry.id), 'tagId':temp[0].id})
                            db.query('UPDATE tags SET entryNum = $entryNum WHERE id = $tagId',
                                    vars={'entryNum':int(temp[0].entryNum) + 1, 'tagId':temp[0].id})
                        else:
                            tagId = db.insert('tags', name = tag.replace("'", "\\'").replace('"', '\\"'), entryNum = 1)
                            db.query('INSERT INTO entry_tag (`entryId`, `tagId`) VALUES ($entryId, $tagId)',
                                    vars={'entryId':int(entry.id), 'tagId':int(tagId)})
                #删除tag
                if tagsDel:
                    for tag in tagsDel:
                        temp = list(db.query("SELECT * FROM tags WHERE LOWER(name) = $name",
                            vars={'name':tag.lower()}))
                        if temp:
                            if temp[0].entryNum == 1:
                                db.query('DELETE FROM tags WHERE id = $tagId',
                                        vars={'tagId':temp[0].id})
                            else:
                                db.query('UPDATE tags SET `entryNum` = $entryNum WHERE id = $tagId',
                                        vars={'entryNum':int(temp[0].entryNum) - 1, 'tagId':temp[0].id})
                            db.query('DELETE FROM entry_tag WHERE entryId = $entryId AND tagId = $tagId',
                                    vars={'entryId':entry.id, 'tagId':temp[0].id})

            if entry.categoryId != f.categoryId.value:
                #原来的category的entryNum-1
                category = list(db.select('categories', where='id=%s' % entry.categoryId))
                if category[0].entryNum > 0:
                    db.update('categories', where='id=%s' % entry.categoryId, entryNum = int(category[0].entryNum)-1)
                #新的category的entryNum+1
                category = list(db.select('categories', where='id=%s' % f.categoryId.value))
                db.update('categories', where='id=%s' % f.categoryId.value, entryNum = int(category[0].entryNum)+1)
            db.update('entries', where='id=%s' % id,
                    modifiedTime = datetime.now(), **f.d
                )
            return web.seeother('/entry/list/')
        else:
            d['f'] = f
            d['entry'] = entry
            return render.entry_edit(**d)

class entry_del(object):
    @login_required
    def GET(self, id):
        entry = list(db.query('SELECT * FROM entries WHERE id = $id', vars={'id':id}))
        if len(entry) > 0:
            db.query('DELETE FROM entries WHERE id = $id', vars={'id':id})
            category = list(db.query('SELECT * FROM categories WHERE id = $id',
                vars={'id':entry[0].categoryId}))
            db.query('UPDATE categories SET `entryNum` = $entryNum WHERE id = $categoryId',
                    vars={'entryNum':int(category[0].entryNum) - 1, 'categoryId':category[0].id})
            tags = list(db.query('SELECT t.id AS tagId, t.entryNum AS entryNum '
                'FROM entry_tag et LEFT JOIN tags t ON t.id = et.tagId '
                'WHERE et.entryId = $entryId', vars= {'entryId':entry[0].id}))
            for tag in tags:
                if tag.entryNum > 2:
                    db.query('UPDATE tags SET `entryNum` = $entryNum WHERE id = $id',
                            vars={'entryNum':int(tag.entryNum) - 1, 'id':tag.tagId})
                if temp[0].entryNum == 1:
                    db.query('DELETE FROM tags WHERE id = $tagId', vars={'tagId':tag.tagId})
                db.query('DELETE FROM entry_tag WHERE entryId = $entryId AND tagId = $tagId',
                        vars={'entryId':tag.entryId, 'tagId':tag.tagId})
        return web.seeother('/entry/')

class links(object):
    @login_required
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
        links = list(db.query('SELECT * FROM links ORDER BY name ASC '
            'LIMIT $start, 10', vars={'start': (page - 1) * 10}))

        para['page'] = page
        para['pages'] = pages
        para['links'] = links

        return render.tag(**para)

class link_add(object):
    @login_required
    def GET(self):
        f = linkForm()

        para['f'] = f

        return render.link_add(**para)

    @login_required
    def POST(self):
        f = linkForm()
        if f.validates():
            data = dict(**f.d)
            db.insert('links', name = data['name'], url = data['url'])
        return web.seeother('/links/')

class link_edit(object):
    @login_required
    def GET(self, id):
        f = linkForm()
        links = list(db.query("SELECT * FROM links WHERE id = $id", vars = {'id':id}))
        f.get('name').value = links[0].name
        f.get('url').value = links[0].slug

        para['f'] = f

        return render.link_edit(**para)

    @login_required
    def POST(self, id):
        f = linkForm()
        if f.validates():
            data = dict(**f.d)
            db.update('links', where = "id = %s" % id, name = data['name'], url = data['url'])
        return web.seeother('/links/')

class link_del(object):
    @login_required
    def GET(self, id):
        db.delete('links', where = 'id = %s' % id)
        return web.seeother('/links/')

class page(object):
    @login_required
    def GET(self):
        pages = list(db.select('pages'))

        para['pages'] = pages

        return render.page(**para)

class page_add(object):
    @login_required
    def GET(self):
        return render.page_add(**para)

    @login_required
    def POST(self):
        data = web.input()
        db.insert('pages', title = data['title'], slug = data['slug'],
                createdTime = datetime.now(), content = data['content'])
        return web.seeother('/page/')

class page_edit(object):
    @login_required
    def GET(self, id):
        page = list(db.select('pages', where='id = %s' % id))
        if not page:
            para['page'] = page[0]
        return render.page_edit(**para)

    @login_required
    def POST(self, id):
        data = web.input(title=None, slug=None, content=None)
        if not title and not slug and not content:
            db.update('pages', where="id = %s" % id, title=data.title, slug=data.slug, content=data.content)
        return web.seeother('/page/')

class page_del(object):
    @login_required
    def GET(self, id):
        db.delete('pages', where='id = %s' % id)
        return web.seeother('/page/')

class reblog(object):
    def GET(self):
        raise web.seeother('/')
