#!/usr/bin/env python2.6
#coding:utf-8

import web
import views
from views import my_loadhook, notfound, internalerror
import admin

urls = (
        '/admin', admin.app_admin,
        '/', 'views.index',
        '^/entry/(.*)/$', 'views.entry',
        '^/category/(.*)/$', 'views.category',
        '^/tag/(.*)/$', 'views.tag',
        '^/add_comment/$', 'views.addComment',
        '^/rss.xml$', 'views.rss',
    )

app = web.application(urls, globals(), autoreload = True)
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'captcha': 0})

app.add_processor(web.loadhook(my_loadhook))
#app.notfound = notfound
#app.internalerror = internalerror

if __name__ == '__main__':
    app.run()
