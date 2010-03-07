#!/usr/bin/env python
#-*-coding:utf-8-*-

import web
import memcache
from web.contrib.template import render_jinja
from templatefilters import avatar, notnull, formnote, content
import os

__all__ = [
        'pageCount', 'db', 'mc', 'render', 'render_admin'    
    ]
pageCount = 5

#数据库配置
db = web.database(dbn = 'mysql', db = 'davidblog_new', user='root', pw = 'root')

#memcache配置
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#render_jinja配置
def getRender():
    render = render_jinja(
        os.getcwd() + '/templates',
        encoding = 'utf-8',
    )
    myFilters = {'avatar':avatar,'notnull':notnull,
        'formnote':formnote, 'content':content}
    render._lookup.filters.update(myFilters)
    return render
render = getRender()

#render_jinja配置 -- admin
def getAdminRender():
    render = render_jinja(
            os.getcwd() + '/templates/admin',
            encoding = 'utf-8',
        )
    myFilters = {'avatar':avatar,'notnull':notnull,
        'formnote':formnote, 'content':content}
    render._lookup.filters.update(myFilters)
    return render
render_admin = getAdminRender()
