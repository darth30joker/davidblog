#!/usr/bin/env python2.6
#coding:utf-8

import web
import views
import admin

urls = (
        '/admin', admin.app_admin,
        '/', 'views.index',    
        '/entry/(.*)/', 'views.entry',    
        '/category/(.*)/', 'views.category',    
        '/tag/(.*)/', 'views.tag',    
        '/add_comment/', 'views.addComment',
        '^/rss.xml$', 'views.rss',
    )

app = web.application(urls, globals(), autoreload = True)
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'captcha': 0})

if __name__ == '__main__':
    app.run()
