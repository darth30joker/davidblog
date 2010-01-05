#!/usr/bin/env python2.6
#coding:utf-8

import web
import views
from views import my_loadhook
import admin

urls = (
        '/admin', admin.app_admin,
        '/', 'views.index',
        '^/entry/(.*)/$', 'views.entry',
        '^/page/(.*)/$', 'views.page',
        '^/category/(.*)/$', 'views.category',
        '^/tag/(.*)/$', 'views.tag',
        '^/add_comment/$', 'views.addComment',
        '^/rss.xml$', 'views.rss',
        '^/test$', 'views.test',
    )

app = web.application(urls, globals(), autoreload = True)
session = web.session.Session(app,
        web.session.DiskStore('sessions'),
        initializer={'captcha': 0, 'isAdmin':0})

app.add_processor(web.loadhook(my_loadhook))
#app.notfound = notfound
#app.internalerror = internalerror

def getSession():
    if not web.config.get('_session'):
        web.config._session = session

if __name__ == '__main__':
    getSession()
    app.run()
