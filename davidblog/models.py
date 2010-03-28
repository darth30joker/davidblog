#-*-coding:utf-8-*-
from datetime import datetime
from sqlalchemy import create_engine, Table, ForeignKey
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relation, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///db.sqlite', echo=False)

Base = declarative_base()
metadata = Base.metadata

entry_tag = Table('entry_tag', metadata,
            Column('entryId', Integer, ForeignKey('entries.id')),
            Column('tagId', Integer, ForeignKey('tags.id'))
        )

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    entryId = Column(Integer, ForeignKey('entries.id'))
    email = Column(String)
    username = Column(String)
    url = Column(String)
    comment = Column(Text)
    createdTime = Column(DateTime)

    def __init__(self, entryId, username, email, url, comment):
        self.entryId = entryId
        self.username = username
        self.email = email
        self.url = url
        self.comment = comment
        self.createdTime = datetime.now()

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    content = Column(Text)
    createdTime = Column(DateTime, default=datetime.now())
    modifiedTime = Column(DateTime, default=datetime.now())
    viewNum = Column(Integer, default=0)
    commentNum = Column(Integer, default=0)

    tags = relation('Tag', secondary=entry_tag, backref='entries')
    comments = relation(Comment, order_by=Comment.createdTime,
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
    name = Column(String, unique=True)
    entryNum = Column(Integer, default=0)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag ('%s')>" % self.name

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    slug = Column(String, unique=True)
    content = Column(Text)
    createdTime = Column(DateTime, default=datetime.now())
    modifiedTime = Column(DateTime, default=datetime.now())

    def __init__(self, title, slug, content):
        self.title = title
        self.slug = slug
        self.content = content

    def __repr__(self):
       return "<Page ('%s')>" % (self.title,)

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String)
    createdTime = Column(DateTime)

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

if __name__ == "__main__":
    metadata.create_all(engine)
