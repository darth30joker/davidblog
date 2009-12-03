#coding=utf-8

from web.contrib import forms

pasteForm = form.Form(
        form.Textbox('title'),
        form.Dropdown('syntax', syntax_list),
        form.Textarea('content'),
    )

username_validate = form.regexp(r".{3,15}$", u"请输入3-15位的用户名")
email_validate = form.regexp(r".*@.*", u"请输入合法的Email地址")
url_validate = form.regexp(r"http://.*", u"请输入合法的URL地址")

commentForm = form.Form(
        form.Textbox('name', username_validate),
        form.Textbox('email', email_validate),
        form.Textbox('url'),
        form.Textarea('comment'),
        form.Button('submit', type="submit", description=u"留言"),
        validators = [
                form.Validator(u"请输入留言内容", lambda i: len(i) == 0)
            ]
    )
