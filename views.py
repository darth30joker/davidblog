#coding:utf-8

import web
from davidblog import render

class index(object):
    def GET(self):
        return render.index()
