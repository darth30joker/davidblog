#-*-coding:utf-8-*-

from datetime import datetime
import hashlib
import web
from forms import *
from settings import pageCount
from settings import render_admin as render 
from utils import Pagination
from models import *

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
        d['tagNum'] = web.ctx.orm.query(Tag).count()
        d['linkNum'] = web.ctx.orm.query(Link).count()
        d['pageNum'] = web.ctx.orm.query(Page).count()
        d['commentNum'] = web.ctx.orm.query(Comment).count()
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
        p = Pagination(entryCount, pageCount, page)
        entries = web.ctx.orm.query(Entry).order_by('entries.created_time DESC')[int(p.start):int(p.start+p.limit)]
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
        f = entryForm()
        if f.validates():
            entry = Entry(f.title.value, f.slug.value, f.content.value)
            entry.created_time = entry.modified_time = datetime.now()
            web.ctx.orm.add(entry)
            try:
                web.ctx.orm.commit()
            except:
                web.ctx.orm.rollback()
            else:
                if i.get('tags') is not None:
                    tags = [i.lstrip().rstrip() for i in i['tags'].split(',')]
                    for tag in tags:
                        t = web.ctx.orm.query(Tag).filter('LOWER(name)=:name').params(name=tag.lower()).first()
                        if t:
                            entry.tags.append(t)
                        else:
                            entry.tags.append(Tag(tag))
        else:
            d['f'] = f
            return render.entry_add(**d)
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
            entry.tagList = ",".join([i.name for i in entry.tags])
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
                originalTags = set([i.name.strip() for i in entry.tags])
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
        entry = web.ctx.orm.query(Entry).filter_by(id=id).first()
        if entry:
            if len(entry.tags) > 0:
                for tag in entry.tags:
                    tagsToDel = list()
                    if tag.entryNum == 1:
                        tagsToDel.append(tag)
                    else:
                        tag.entryNum = tag.entryNum - 1
                    entry.tags.remove(tag)
            web.ctx.orm.delete(entry)
            if len(tagsToDel) > 0:
                for i in tagsToDel:
                    web.ctx.orm.delete(i)
        return web.seeother('/entry/list/')

class link_list(object):
    @login_required
    def GET(self):
        page = web.input(page=1)
        try:
            page = int(page.page)
        except:
            page = 1
        linkCount = web.ctx.orm.query(Link).count()
        p = Pagination(linkCount, pageCount, page)
        links = web.ctx.orm.query(Link).order_by('links.name ASC')[int(p.start):int(p.start+p.limit)]
        d['p'] = p
        d['links'] = links
        return render.link_list(**d)

class link_add(object):
    @login_required
    def GET(self):
        f = linkForm()
        d['f'] = f
        return render.link_add(**d)

    @login_required
    def POST(self):
        f = linkForm()
        if f.validates():
            link = Link()
            link.name = f.name.value
            link.description = f.description.value
            link.url = f.url.value
            web.ctx.orm.add(link)
            try:
                web.ctx.orm.commit()
            except:
                web.ctx.orm.rollback()
            return web.seeother('/link/list/')
        else:
            d['f'] = f
            return render.link_add(**d)

class link_edit(object):
    def getLink(self, id):
        return web.ctx.orm.query(Link).filter_by(id=id).first()

    @login_required
    def GET(self, id):
        f = linkForm()
        link = self.getLink(id)
        f.name.value = link.name
        f.url.value = link.url
        f.description.value = link.description
        d['f'] = f
        d['link'] = link
        return render.link_edit(**d)

    @login_required
    def POST(self, id):
        f = linkForm()
        if f.validates():
            link = self.getLink(id)
            link.name = f.name.value
            link.url = f.url.value
            link.description = f.description.value
            return web.seeother('/link/list/')
        else:
            d['f'] = f
            return render.link_edit(**d)

class link_del(object):
    @login_required
    def GET(self, id):
        link = web.ctx.orm.query(Link).filter_by(id=id).first()
        web.ctx.orm.delete(link)
        return web.seeother('/link/list/')

class page_list(object):
    @login_required
    def GET(self):
        pages = web.ctx.orm.query(Page).all()
        d['pages'] = pages
        return render.page_list(**d)

class page_add(object):
    @login_required
    def GET(self):
        d['f'] = pageForm()
        return render.page_add(**d)

    @login_required
    def POST(self):
        i = web.input()
        f = pageForm()
        if f.validates():
            page = Page(f.title.value, f.slug.value, f.content.value)
            web.ctx.orm.add(page)
            return web.seeother('/page/list/')
        else:
            d['f'] = f
            return render.page_add(**d)

class page_edit(object):
    def getPage(self, id):
        return web.ctx.orm.query(Page).filter_by(id=id).first()

    @login_required
    def GET(self, id):
        page = self.getPage(id)
        f = pageForm()
        if page:
            d['page'] = page
            d['f'] = f
        return render.page_edit(**d)

    @login_required
    def POST(self, id):
        page = self.getPage(id)
        f = pageForm()
        if f.validates():
            page.title = f.title.value
            page.slug = f.slug.value
            page.content = f.content.value
            page.modifiedTime= datetime.now()
            return web.seeother('/page/list/')
        else:
            d['f'] = f
            return render.page_edit(**d)

class page_del(object):
    @login_required
    def GET(self, id):
        page = web.ctx.orm.query(Page).filter_by(id=id).first()
        if page:
            web.ctx.orm.delete(page)
        return web.seeother('/page/')

