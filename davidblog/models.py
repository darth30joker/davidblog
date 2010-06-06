#-*-coding:utf-8-*-
from datetime import datetime
from sqlalchemy import create_engine, Table, ForeignKey
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

#engine = create_engine('sqlite:///db.sqlite', echo=False)
engine = create_engine('mysql://root:root@localhost/davidblog?charset=utf8', echo=False)

Base = declarative_base()
metadata = Base.metadata

entry_tag = Table('entry_tag', metadata,
            Column('entry_id', Integer, ForeignKey('entries.id')),
            Column('tag_id', Integer, ForeignKey('tags.id'))
        )

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    entry_id = Column(Integer, ForeignKey('entries.id'))
    email = Column(String(50))
    username = Column(String(50))
    url = Column(String(50))
    comment = Column(Text)
    created_time = Column(DateTime)

    def __init__(self, entry_id, username, email, url, comment):
        self.entry_id = entry_id
        self.username = username
        self.email = email
        self.url = url
        self.comment = comment
        self.created_time = datetime.now()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    slug = Column(String(255), unique=True)
    content = Column(Text)
    created_time = Column(DateTime, default=datetime.now())
    modified_time = Column(DateTime, default=datetime.now())
    view_num = Column(Integer, default=0)
    comment_num = Column(Integer, default=0)

    tags = relation('Tag', secondary=entry_tag, backref='entries')
    comments = relation(Comment, order_by=Comment.created_time,
                backref="entries"
            )

    def __init__(self, title, slug, content):
        self.title = title
        self.slug = slug
        self.content = content

    def __repr__(self):
       return "<Entry ('%s')>" % self.id

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    entry_num = Column(Integer, default=0)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag ('%s')>" % self.name

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    slug = Column(String(255), unique=True)
    content = Column(Text)
    created_time = Column(DateTime, default=datetime.now())
    modified_time = Column(DateTime, default=datetime.now())

    def __init__(self, title, slug, content):
        self.title = title
        self.slug = slug
        self.content = content

    def __repr__(self):
       return "<Page ('%s')>" % (self.title,)

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    name = Column(String(45))
    url = Column(String(45))
    description = Column(String(255))
    created_time = Column(DateTime, default=datetime.now())

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String(45))
    password = Column(String(45))

if __name__ == "__main__":
    metadata.create_all(engine)
