#-*-coding:utf-8-*-
import hashlib
from markdown import markdown
 
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

def content(value):
    return markdown(value)
