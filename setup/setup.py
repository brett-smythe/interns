from sqlalchemy import create_engine

import schema

db_user_name = 'eleanor'
db_password = 'is there life on mars'
db_ip_addy = 'localhost'
db_name = 'eleanor'

engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(db_user_name, db_password, db_ip_addy, db_name))
schema.Base.metadata.create_all(engine)

