#!/usr/bin/env python
#coding:utf-8

import web
import memcache
from web.contrib.template import render_mako
import os

#数据库配置
db = web.database(dbn = 'mysql', db = 'davidblog', user='root', pw = 'root')

#memcache配置
mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#render_mako配置
render = render_mako(
        directories = [os.getcwd() + '/templates'],
        input_encoding = 'utf-8',
        output_encoding = 'utf-8',
    )

#render_mako配置 -- admin
render_admin = render_mako(
        directories = [os.getcwd() + '/templates/admin'],
        input_encoding = 'utf-8',
        output_encoding = 'utf-8',
    )
