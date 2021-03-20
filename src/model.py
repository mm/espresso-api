from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, post_load, EXCLUDE
from src.exceptions import InvalidUsage
from src.helpers import extract_title_from_url

# Initially, the database isn't bound to an app. This is so
# we can bind to one while our app is being created in our
# app factory.
db = SQLAlchemy()

# ORM Models:

class User(db.Model):
    """Represents a user in the database."""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(512), nullable=True)

    # Generally sourced from Firebase:
    email = db.Column(db.String(255), nullable=True)
    external_uid = db.Column(db.String(255), nullable=True)
    
    links = db.relationship('Link', backref='user', lazy=True)

    def __repr__(self):
        return '<User: {} [{}]>'.format(self.name, self.id)

    @classmethod
    def create(cls, name, api_key=None, firebase_uid=None, email=None) -> int:
        """Creates a new user and returns that user's ID.
        Optionally an API key (hashed) can be specified, useful in
        testing.
        """
        new_user = User(
            name=name,
            api_key=api_key,
            external_uid=firebase_uid,
            email=email
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            # TODO: Add exception logging in here
            raise
        return new_user.id


    def create_link(self, url=None, title=None, **kwargs):
        """Adds a link to the database for the given user.
        If the title attribute is None, will call a helper function to
        attempt to scrape the title from the HTML of the website passed in.
        Will also raise an exception if the URL ended up being invalid.

        Returns the ID of the link entry in the database if successful.
        """
        
        # Load into the Link schema to catch any errors. We'll catch ValidationErrors
        # at the blueprint level:
        errors = LinkSchema().validate(dict(user_id=self.id, title=title, url=url))
        if errors:
            raise ValidationError(message=errors)

        # Try and extract our title from the URL if it's not provided.
        # If the title can't be extracted, a value of None is still okay.
        if title is None:
            title = extract_title_from_url(url)

        # Add this link to the database:
        link = Link(user_id=self.id, title=title, url=url)
        db.session.add(link)
        db.session.commit()
        return link.id

    @classmethod
    def user_at_uid(cls, uid: str):
        return cls.query.filter_by(external_uid=uid).first()


class Link(db.Model):
    """Represents a link stored in the database. All datetimes are stored as UTC.
    """
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    url = db.Column(db.String(2048), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(512), nullable=True)
    read = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return '<Link: {} [{}]>'.format(self.url, self.id)


# Schema:

class UserSchema(Schema):
    id = fields.Int(strict=True, required=True)
    name = fields.Str()
    # Setting api_key as load_only ensures any dumps don't contain it:
    api_key = fields.Str(required=True, load_only=True)


class LinkSchema(Schema):

    class Meta:
        # Ignore everything passed in that isn't listed here
        unknown = EXCLUDE

    id = fields.Int(strict=True, dump_only=True)
    date_added = fields.DateTime(format="%Y-%m-%d %H:%M")
    url = fields.URL(required=True, relative=False, require_tld=True)
    user_id = fields.Int(strict=True, required=True, load_only=True)
    title = fields.Str(allow_none=True)
    read = fields.Bool(default=False)
    category = fields.Str(allow_none=True)

    @post_load
    def make_link(self, data, **kwargs):
        return Link(**data)
