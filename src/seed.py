"""Seeds the database with some sample links and a test API key.
"""

from src.model import db, User, Link
from src.auth.service import AuthService
from colorama import init, Fore, Style

auth_service = AuthService()

SEED_LINKS = [
    {
        'url': 'https://postgresql.com',
        'title': 'PostgreSQL'
    },
    {
        'url': 'https://www.nytimes.com/ca/',
        'title': 'The New York Times Canada'
    },
    {
        'url': 'https://app.swaggerhub.com/help/tutorials/openapi-3-tutorial',
        'title': 'OpenAPI 3.0 Tutorial'
    },
    {
        'url': 'https://docs.python.org/3/',
        'title': '3.9.1 Documentation'
    },
    {
        'url': 'https://docs.netlify.com/',
        'title': 'Welcome to Netlify | Netlify Docs'
    },
    {
        'url': 'https://developer.mozilla.org/en-US/docs/Learn',
        'title': 'Learn Web Development | MDN'
    },
    {
        'url': 'https://www.digitalocean.com/docs/',
        'title': 'DigitalOcean Product Documentation'
    },
    {
        'url': 'https://git-scm.com/',
        'title': 'Git'
    },
    {
        'url': 'https://dev.to/mmascioni',
        'title': 'Matthew Mascioni - DEV Community 👩‍💻🧑‍💻'
    }
]

init(autoreset=True)

def seed_user(name="Matt"):
    """Create a user and API key in the database. Returns a 2-member
    tuple of (User ID, User API Key)
    """
    print(Fore.CYAN + 'Creating an initial user...')
    api_pair = auth_service.generate_api_key()
    print(Style.BRIGHT + f'API key generated: {api_pair.api_key}')
    user_id = User.create(name=name, api_key=api_pair.hashed_key)
    print(Fore.GREEN + f'User ID: {user_id}')
    return user_id, api_pair.api_key


def seed_links(id):
    """Seeds initial links underneath the seed user (given by
    ID)
    """

    if not id:
        print(Fore.RED + 'User must be created first!')
        return None

    user = User.query.get(id)

    for link in SEED_LINKS:
        link_id = user.create_link(**link)
        if link_id:
            print(Fore.CYAN + f'Created link with ID: {link_id}')
    
    print(Fore.GREEN + 'Links seeded successfully.')


def seed_dummy_data():
    """Calls both seed_user() and seed_links() to generate
    a complete development environment with dummy data.
    """

    user_id, api_key = seed_user()
    seed_links(user_id)