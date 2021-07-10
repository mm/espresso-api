"""Seeding functions used to create a QA environment or get
the application started. 
"""

from faker import Faker
from faker.providers import internet, date_time, company, misc
from src.model import User, Link, db
from src.auth.service import AuthService
from typing import List, Tuple

fake = Faker("en_US")
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(company)
fake.add_provider(misc)


def seed_self(email: str, name: str = None, external_uid: str = None) -> Tuple[User, str]:
    """Seeds a dummy record with your email (can be useful
    for Firebase syncing later). Also returns an API key generated
    for the user.
    """
    api_key = AuthService.generate_api_key()
    if not name:
        name = fake.name()
    user_id = User.create(name=name, email=email, api_key=api_key.hashed_key, firebase_uid=external_uid)
    return (user_id, api_key.api_key)


def seed_fake_users(num_users: int = 30) -> List[User]:
    users = []
    for _ in range(num_users):
        key = AuthService.generate_api_key()
        user = User(
            name=fake.name(), email=fake.ascii_free_email(), api_key=key.hashed_key
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()
    return users


def seed_links(user_id: int, num_links: int = 30):
    for _ in range(num_links):
        link = Link(
            user_id=user_id,
            date_added=fake.date_time_between(start_date="-2y"),
            url=fake.uri(),
            title=fake.catch_phrase(),
            read=fake.boolean(chance_of_getting_true=50),
        )
        db.session.add(link)
    db.session.commit()


def seed_api_key(user_id: int) -> str:
    """Generates an API key for a given test user at a given
    user ID
    """
    user = User.query.get(user_id)
    api_keyset = AuthService.generate_api_key()
    user.api_key = api_keyset.hashed_key
    return api_keyset.api_key
