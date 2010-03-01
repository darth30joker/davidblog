#-*-coding=utf-8-*-
import web
from web import form

__all__ = [
        'commentForm', 'linkForm'
    ]

username_validate = form.regexp(r".{3,15}$", u"请输入3-15位的用户名")
email_validate = form.regexp(r".*@.*", u"请输入合法的Email地址")
url_validate = form.regexp(r"http://.*", u"请输入合法的URL地址")
captchaValidator = form.Validator('Captcha Code',
        lambda x: x == web.ctx.session.captcha)

commentForm = form.Form(
        form.Textbox('username', form.notnull, username_validate),
        form.Textbox('email', form.notnull, email_validate),
        form.Textbox('url'),
        form.Textarea('comment', form.notnull),
        form.Textbox('captcha', captchaValidator),
        form.Button('submit', type="submit", description=u"留言"),
    )

categoryForm = form.Form(
        form.Textbox('name', form.notnull),
        form.Textbox('slug', form.notnull),
        form.Button('submit', type="submit", description = u"添加")
    )

linkForm = form.Form(
        form.Textbox('name', form.notnull),
        form.Textbox('url', form.notnull, url_validate),
        form.Button('submit', type="submit", description = u"添加")
    )
