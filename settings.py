#!/usr/bin/env python
#-*-coding:utf-8-*-

import web
import memcache
from web.contrib.template import render_jinja
from templatefilters import avatar, notnull, formnote
import os

__all__ = [
        'pageCount', 'db', 'mc', 'render', 'render_admin'    
    ]
pageCount = 5

#数据库配置
db = web.database(dbn = 'mysql',
        db = 'davidblog',
        user = 'root',
        pw = 'root',
        charset = 'utf8')

#memcache配置
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#render_mako配置
def getRender():
    render = render_jinja(
        os.getcwd() + '/templates',
        encoding = 'utf-8',
    )
    myFilters = {'avatar':avatar,'notnull':notnull,'formnote':formnote}
    render._lookup.filters.update(myFilters)
    return render
render = getRender()

#render_mako配置 -- admin
render_admin = render_jinja(
        os.getcwd() + '/templates/admin',
        encoding = 'utf-8'
    )
