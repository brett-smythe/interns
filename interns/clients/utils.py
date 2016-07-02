from datetime import datetime

from dateutil.parser import parse as date_parse

from interns.clients.db_client import GetDBSession
from interns.models import models
from interns.utils import get_logger


logger = get_logger(__name__)


def insert_text_data(data_source, source_url, text, time_posted, session):
    """Adds the base entry for a text data source to the database and returns
    the newly created model

    
    Keyword arguments:
    data_source -- An enum indicating source. The enum is located in
    interns.models.models.AllowedSources
    source_url -- A string indicating the url the text was pulled from
    text -- the raw text data pulled from the url
    time_posted -- either a datetime object or a datetime string
    session -- active db session
    """
    if not isinstance(time_posted, datetime):
        time_posted = date_parse(time_posted)

    logger.debug('Inserting text data into postgres')
    
    TextModel = models.TextSource(
        source_key=data_source,
        source_url=source_url,
        written_text=text,
        time_posted=time_posted
    )

    session.add(TextModel)
    return TextModel

