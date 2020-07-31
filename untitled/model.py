from datetime import datetime
from pytz import timezone
from flask_sqlalchemy import SQLAlchemy

# Initially, the database isn't bound to an app. This is so
# we can bind to one while our app is being created in our
# app factory.
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
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().replace(tzinfo=timezone('America/Toronto')))
    url = db.Column(db.String(2048), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(512), nullable=True)
    read = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Link: {} [{}]>'.format(self.url, self.id)

    def to_dict(self):
        """Returns a dict representation of a saved link.
        """
        return {
            'id': self.id,
            'date_added': self.date_added.strftime('%Y-%m-%d %I:%M %p %Z'),
            'url': self.url,
            'title': self.title,
            'read': self.read
        }

    @classmethod
    def create_link(url, title=None):
        """Adds a link to the database. If the title attribute is None,
        will call a helper function to attempt to scrape the title from
        the HTML of the website passed in. Will also raise an exception
        if the URL ended up being invalid.
        """
        pass