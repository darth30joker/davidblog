#coding=utf-8

from web.contrib import forms

pasteForm = form.Form(
        form.Textbox('title'),
        form.Dropdown('syntax', syntax_list),
        form.Textarea('content'),
    )
