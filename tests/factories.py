import factory
from src.model import Link, User, db
from hashlib import sha256


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.Faker("email")
    api_key = factory.Faker("uuid4", cast_to=str)


class LinkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Link
        sqlalchemy_session = db.session

    date_added = factory.Faker("date_time")
    id = factory.Sequence(lambda n: n + 1)
    url = factory.Faker("uri")
    title = factory.Faker("catch_phrase")
    read = factory.Faker("boolean")
    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
