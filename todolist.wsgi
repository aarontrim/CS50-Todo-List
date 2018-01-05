import sys
import os
sys.path.insert(0, '/var/www/todolist')
os.environ['SECRET_KEY']='4avo2OdM4N8h'
from application import app as application
