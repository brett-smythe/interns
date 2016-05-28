from interns.models import models, twitter_models
from interns.models.base import Base

from interns.clients.db_client import engine

Base.metadata.create_all(engine)

