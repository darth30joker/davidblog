#!/usr/bin/env python2.6
#coding:utf-8

import web
import adminviews

urls = (
        '', 'adminviews.back',    
        '/$', 'adminviews.index',
        '/login/', 'adminviews.login',
        '/logout/', 'adminviews.logout',
        '/link/list/', 'adminviews.link_list',
        '/link/add/', 'adminviews.link_add',
        '/link/del/(.*)/', 'adminviews.link_del',
        '/link/edit/(.*)/', 'adminviews.link_edit',
        '/tag/list/', 'adminviews.tag_list',
        '/tag/add/', 'adminviews.tag_add',
        '/tag/del/(.*)/', 'adminviews.tag_del',
        '/tag/edit/(.*)/', 'adminviews.tag_edit',
        '/entry/list/', 'adminviews.entry_list',
        '/entry/add/', 'adminviews.entry_add',
        '/entry/del/(.*)/', 'adminviews.entry_del',
        '/entry/edit/(.*)/', 'adminviews.entry_edit',
        '/page/list/', 'adminviews.page_list',
        '/page/add/', 'adminviews.page_add',
        '/page/del/(.*)/', 'adminviews.page_del',
        '/page/edit/(.*)/', 'adminviews.page_edit',
    )

app_admin = web.application(urls, globals(), autoreload = True)
app_admin.add_processor(web.loadhook(adminviews.my_loadhook))
