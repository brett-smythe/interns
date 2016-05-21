from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TextSource(Base):
    __tablename__ = 'text_source'

    id = Column(Integer, primary_key=True)
    source_key = Column(String)
    source_url = Column(String)
    written_text = Column(Text)
    time_posted = Column(DateTime)

