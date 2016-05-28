import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship

from base import Base


class AllowedSources(enum.Enum):
    twitter = 'twitter'


class TextSource(Base):
    __tablename__ = 'text_source'

    id = Column(Integer, primary_key=True)
    source_key = Column(
        Enum(
            AllowedSources.twitter.name, name='allowed_sources'
        )
    )
    source_url = Column(String)
    written_text = Column(Text)
    time_posted = Column(DateTime)

    twitter_source = relationship(
        'TwitterSource',
        back_populates='text_source',
        cascade='all, delete, delete-orphan',
        uselist=False
    )

