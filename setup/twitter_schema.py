from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

#from schema import TextSource
from base import Base

class TwitterSource(Base):
    __tablename__ = 'twitter_source'

    id = Column(Integer, primary_key=True)
    tweet_origin_screen_name = Column(String)
    text_source_id = Column(Integer, ForeignKey('text_source.id'), nullable = False)
    hastags = Column(String)
    urls = Column(String)
    user_names = Column(String)
    
