#!/usr/bin/env python2.6
#coding:utf-8

import web
import views
import admin

urls = (
        '/admin', admin.app_admin,
        '/', 'views.index',
        '^/entry/(.*)/$', 'views.entry',
        '^/page/(.*)/$', 'views.page',
        '^/tag/(.*)/$', 'views.tag',
        '^/captcha/$', 'views.captcha',
        '^/rss.xml$', 'views.rss',
    )

app = web.application(urls, globals())
session = web.session.Session(
        app, web.session.DiskStore('sessions'),
        initializer={'captcha': 0, 'isAdmin':0})

app.add_processor(web.loadhook(views.my_loadhook))
app.add_processor(views.my_handler)
app.notfound = views.notfound
app.internalerror = views.internalerror

def getSession():
    if '_session' not in web.config:
        web.config._session = session

if __name__ == '__main__':
    getSession()
    app.run()
