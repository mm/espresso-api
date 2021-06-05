import factory
from src.model import Link, User, Collection, db


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session

    id = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("name")
    email = factory.Faker("email")
    api_key = factory.Faker("uuid4", cast_to=str)

class CollectionFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Collection
        sqlalchemy_session = db.session
        exclude = ['user']

    date_added = factory.Faker("date_time")
    id = factory.Sequence(lambda n: n + 1)
    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
    archived = factory.Faker("boolean")
    icon = factory.Faker("random_choices", elements=[':face with raised eyebrow:', ':cold face:'])
    order = factory.Sequence(lambda n: n + 1)
    name = factory.Faker("word")

class LinkFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Link
        sqlalchemy_session = db.session
        exclude = ['collection']

    date_added = factory.Faker("date_time")
    id = factory.Sequence(lambda n: n + 1)
    url = factory.Faker("uri")
    title = factory.Faker("catch_phrase")
    read = factory.Faker("boolean")
    user = factory.SubFactory(UserFactory)
    user_id = factory.SelfAttribute("user.id")
    collection = factory.SubFactory(CollectionFactory)
    collection_id = factory.SelfAttribute("collection.id")
