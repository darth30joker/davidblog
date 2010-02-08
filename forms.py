#-*-coding=utf-8-*-

import web
from web import form
from settings import db

__all__ = [
        'loginForm', 'commentForm', 'categoryForm',
        'linkForm', 'entryForm'
    ]

usernameValidator = form.regexp(r".{3,15}$", "Username must be 3-15 charactors")
emailValidator = form.regexp(r".*@.*", 'Please input a valid email address')
urlValidator = form.regexp(r"http://.*", "Please input a valid url address")
captchaValidator = form.Validator('Captcha Code',
        lambda x: x == web.config._session.captcha)

def passwordValidator(i):
    user = list(db.query('SELECT * FROM admins WHERE username = $username',
        vars={'username': i.username}))[0]
    return hashlib.md5(i.password).hexdigest() == user.password
    
loginForm = form.Form(
        form.Textbox('username',
            form.notnull, usernameValidator),
        form.Password('password',
            form.notnull),
        validators = [
            form.Validator('Username/Password wrong!', passwordValidator)
        ]
    )

commentForm = form.Form(
        form.Textbox('username',
            form.notnull, usernameValidator),
        form.Textbox('email',
            form.notnull, emailValidator),
        form.Textbox('url'),
        form.Textbox('captcha', captchaValidator,
            description="Captcha Code"),
        form.Textarea('comment', form.notnull),
    )

categoryForm = form.Form(
        form.Textbox('name', form.notnull),
        form.Textbox('slug', form.notnull)
    )

linkForm = form.Form(
        form.Textbox('name', form.notnull),
        form.Textbox('url', form.notnull, urlValidator)
    )

entryForm = form.Form(
        form.Textbox('title', form.notnull),
        form.Textbox('content', form.notnull),
        form.Textbox('slug', form.notnull),
        form.Textarea('categoryId', form.notnull),
    )
