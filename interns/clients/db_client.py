from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

db_user_name = 'eleanor'
db_password = 'is there life on mars'
db_ip_addy = '192.168.1.122'
db_name = 'eleanor'

engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(db_user_name, db_password, db_ip_addy, db_name))


class GetDBSession(object):

    def __enter__(self):
        Session = sessionmaker(bind = engine)
        self.session = Session()
        return self.session

    def __exit__(self, exc_type, exc_value, traceback):
        # the above args should be == None if there are no exceptions so:
        if ((exc_type != None) and (exc_value != None) and (traceback != None)):
            # TODO add logging here
            self.session.rollback()
        self.session.close()

