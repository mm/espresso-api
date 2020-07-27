from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(512), nullable=False)
    links = db.relationship('Link', backref='user', lazy=True)

    def __repr__(self):
        return '<User: {} [{}]>'.format(self.name, self.id)
    

class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now())
    url = db.Column(db.String(2048), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(512), nullable=True)
    read = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Link: {} [{}]>'.format(self.url, self.id)