#-*-coding:utf-8-*-

from datetime import datetime
import hashlib
import web
from forms import *
from settings import pageCount
from settings import render_admin as render 
from utils import Pagination

d = {}

def my_loadhook():
    pass

def login_required(func):
    def Function(*args):
        if web.ctx.session.isAdmin == 0:
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
        d['entryNum'] = web.ctx.orm.query(Entry).count()
        d['commentNum'] = web.ctx.orm.query(Comment).count()
        d['tagNum'] = web.ctx.orm.query(Tag).count()
        d['linkNum'] = web.ctx.orm.query(Link).count()
        return render.index(**d)

class login(object):
    def GET(self):
        return render.login(**d)

    def POST(self):
        i = web.input(username=None, password=None)
        if i.username and i.password:
            admin = web.ctx.orm.query(Admin).filter_by(username=i.username).first()
            if admin:
                if hashlib.md5(i.password).hexdigest() == admin.password:
                    web.ctx.session.isAdmin = 1
                    raise web.seeother('/')
        d['error'] = "Wrong username/password!"
        return render.login(**d)

class logout(object):
    def GET(self):
        web.ctx.session.kill()
        raise web.seeother('/')

class entry_list(object):
    @login_required
    def GET(self):
        i = web.input(page=1)
        try:
            page = int(i.page)
        except:
            page = 1
        entryCount = web.ctx.orm.query(Entry).count()
        p = Pagination(entryCount, pageCount, i.page)
        entries = web.ctx.orm.query(Entry).order_by('entries.createdTime DESC')[p.start:p.start+p.limit]
        d['p'] = p
        d['entries'] = entries
        return render.entry_list(**d)

class entry_add(object):
    @login_required
    def GET(self):
        d['f'] = entryForm()
        return render.entry_add(**d)

    @login_required
    def POST(self):
        i = web.input(tags = None)
        if f.validates():
            entry = Entry(f.title.value, f.slug.value, f.content.value)
            web.ctx.orm.add(Entry)
        if i.get('tags') is not None:
            tags = [i.lstrip().rstrip() for i in i['tags'].split(',')]
            for tag in tags:
                t = web.ctx.orm.query(Tag).filter('LOWER(name)=:name').params(name=tag.lower()).first()
                if t:
                    entry.tags.append(t)
                else:
                    entry.tags.append(Tag(tag))
        return web.seeother('/entry/list/')

class entry_edit(object):
    @login_required
    def getEntry(self, id):
        return web.ctx.orm.query(Entry).filter_by(id=id).first()

    @login_required
    def GET(self, id):
        entry = self.getEntry(id)
        if entry:
            f = entryForm()
            d['entry'] = entry
            d['f'] = f
            return render.entry_edit(**d)

    @login_required
    def POST(self, id):
        f = entryForm()
        entry = self.getEntry(id)
        i = web.input(tags=None)
        if f.validates():
            if i.tags is not None:
                newTags = set([i.strip() for i in i.tags.split(',')])
                originalTags = set([i.strip() for i in entry.tags.split(',')])
                tagsAdd = list(newTags - originalTags)
                tagsDel = list(originalTags - newTags)
                #添加tag
                if tagsAdd:
                    for tag in tagsAdd:
                        t = web.ctx.orm.query(Tag).filter('LOWER(name)=:name').params(name=tag).first()
                        if t:
                            entry.tags.append(t)
                        else:
                            entry.tags.append(Tag(tag))
                #删除tag
                if tagsDel:
                    for tag in tagsDel:
                        t = web.ctx.orm.query(Tag).filter('LOWER(name)=:name').params(name=tag).first()
                        if t:
                            if t.entryNum == 1:
                                web.ctx.orm.delete(t)
                            else:
                                t.entryNum = t.entryNum - 1
                            entry.tags.remove(t)
            entry.title = f.title.value
            entry.slug = f.slug.value
            entry.content = f.content.value
            entry.modifiedTime = datetime.now()
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

