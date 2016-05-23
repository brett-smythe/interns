import schema
import twitter_schema

from base import Base

from db_conn import engine

Base.metadata.create_all(engine)

