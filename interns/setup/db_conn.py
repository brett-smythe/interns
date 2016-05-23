from sqlalchemy import create_engine

db_user_name = 'eleanor'
db_password = 'is there life on mars'
db_ip_addy = '192.168.1.122'
db_name = 'eleanor'

engine = create_engine('postgresql://{0}:{1}@{2}/{3}'.format(db_user_name, db_password, db_ip_addy, db_name))

