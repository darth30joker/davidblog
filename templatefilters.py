#-*-coding:utf-8-*-
import hashlib

def avatar(value):
    return hashlib.md5(value.lower()).hexdigest()

def notnull(value):
    if value:
        return value
    else:
        return ''

def formnote(value):
    if value:
        return '<span class="wrong">' + value + '</span>'
    else:
        return ''
