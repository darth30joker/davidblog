#!/usr/bin/env python2.6
#coding:utf-8

import web
import adminviews

urls = (
        '', 'adminviews.reblog',    
        '/', 'adminviews.index',
        '/categories/', 'adminviews.categories',
        '/category/add/', 'adminviews.category_add',
        '/category/del/(.*)/$', 'adminviews.category_del',
        '/category/edit/(.*)/$', 'adminviews.category_edit',
    )

app_admin = web.application(urls, globals(), autoreload = True)
session = web.session.Session(app_admin, web.session.DiskStore('sessions'), initializer={'captcha': 0})
