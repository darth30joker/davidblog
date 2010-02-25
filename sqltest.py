from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker, backref, relation
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db')
Base = declarative_base()
metadata = Base.metadata

entry_tag = Table('entry_tag', metadata,
        Column('entry_id', Integer, ForeignKey('entries.id')),
        Column('tag_id', Integer, ForeignKey('tags.id')),
    )

class Entry(Base):
    __tablename__ = 'entries'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    tags = relation('Tag', secondary=entry_tag, backref='entries')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Entry ('%s')>" % self.name

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag ('%s')>" % self.name

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    metadata.create_all(engine)
