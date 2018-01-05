''' Database functions using sqlalchemy
'''

import os
from flask_sqlalchemy import SQLAlchemy

from models import db

def init_db():
    ''' Performs initialisation of the database and creates it if it doesn't exist
    '''
    engine = create_engine('sqlite:///database.db')
    if not os.path.exists("database.db"):
        create_db(engine)
    
    return engine

def create_db(engine):
    ''' Creates an empty database in correct structure
    '''
    Base.metadata.create_all(engine)