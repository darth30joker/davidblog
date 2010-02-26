#!/usr/bin/env python
#coding:utf-8

import web
import memcache
from web.contrib.template import render_jinja
import os

pageCount = 5

#数据库配置
db = web.database(dbn = 'mysql', db = 'davidblog_new', user='root', pw = 'root')

#memcache配置
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#render_mako配置
render = render_jinja(
        os.getcwd() + '/templates',
        encoding = 'utf-8',
    )

#render_mako配置 -- admin
render_admin = render_jinja(
        os.getcwd() + '/templates/admin',
        encoding = 'utf-8',
    )
