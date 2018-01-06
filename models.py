''' SQLAlchemy models
'''
from flask_sqlalchemy import SQLAlchemy

from application import app

db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	# model for table of website user information
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(250), nullable=False)
	password = db.Column(db.String(250), nullable=False)
	temporary = db.Column(db.Integer, nullable=False) # boolean flag for whether this is a temporary user
	date_created = db.Column(db.String(11), nullable=False)

	def __repr__(self):
		return '<User %r>' % self.name

class Item(db.Model):
	__tablename__ = 'items'
	# model for table fo todo items
	id = db.Column(db.Integer, primary_key=True)
	userid = db.Column(db.ForeignKey("users.id")) # user owner of this item
	parentid = db.Column(db.ForeignKey("items.id"), default=None) # parent
	text = db.Column(db.String(1000))
	rank = db.Column(db.Integer, default=0)

	def __repr__(self):
		return '<Item %r>' % self.text[:100]