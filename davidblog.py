#!/usr/bin/env python2.6
#coding:utf-8

import web
from web.contrib.template import render_mako
import views

urls = (
        '/', 'views.index',    
        '/entry/(.*)/', 'views.entry',    
        '/category/(.*)/', 'views.category',    
        '/tag/(.*)/', 'views.tag',    
    )

app = web.application(urls, globals(), autoreload = True)

render = render_mako(
        directories = ['templates'],
        input_encoding = 'utf-8',
        output_encoding = 'utf-8',
    )

if __name__ == '__main__':
    #web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()
