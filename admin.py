#!/usr/bin/env python2.6
#coding:utf-8

import web
import adminviews

urls = (
        '', 'adminviews.reblog',    
        '/', 'adminviews.index',
        '/login/', 'adminviews.login',
        '/logout/', 'adminviews.logout',
        '/categories/', 'adminviews.categories',
        '/category/add/', 'adminviews.category_add',
        '/category/del/(.*)/$', 'adminviews.category_del',
        '/category/edit/(.*)/$', 'adminviews.category_edit',
        '/tags/', 'adminviews.tags',
        '/tag/add/', 'adminviews.tag_add',
        '/tag/del/(.*)/$', 'adminviews.tag_del',
        '/tag/edit/(.*)/$', 'adminviews.tag_edit',
        '/entry/', 'adminviews.entry',
        '/entry/add/', 'adminviews.entry_add',
        '/entry/del/(.*)/$', 'adminviews.entry_del',
        '/entry/edit/(.*)/$', 'adminviews.entry_edit',
        '/page/', 'adminviews.page',
        '/page/add/', 'adminviews.page_add',
        '/page/del/(.*)/$', 'adminviews.page_del',
        '/page/edit/(.*)/$', 'adminviews.page_edit',
    )

app_admin = web.application(urls, globals(), autoreload = True)
session = web.session.Session(app_admin, web.session.DiskStore('sessions'), initializer={'isLogin': 0})
