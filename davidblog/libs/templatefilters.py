#-*-coding:utf-8-*-
import hashlib
import re
from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
 
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
    content = markdown(value)
    codes = re.findall('<code>.*?</code>', content, re.U | re.S)
    for i in codes:
        syntax = re.search('#syntax#\w+#/syntax#', i, re.U | re.S)
        if syntax:
            code = i[i.index('#/syntax#') + 9:-7]
        else:
            code = i[6:-7]
        try:
            lexer = get_lexer_by_name(syntax.group()[8:-9], stripall=True)
        except:
            lexer = get_lexer_by_name('c', stripall=True)
        code = highlight(
                code,
                lexer,
                HtmlFormatter(linenos=False, cssclass="syntax"))
        content = content.replace(i, code)
    return content
