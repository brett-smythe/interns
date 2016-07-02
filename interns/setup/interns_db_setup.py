from interns.models import models, twitter_models
from interns.models.base import Base

from interns.clients.db_client import engine
from interns.utils import get_logger

logger = get_logger(__name__)
logger.info('Setting up database for interns')

Base.metadata.create_all(engine)

