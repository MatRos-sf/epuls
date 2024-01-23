from factory.django import DjangoModelFactory
from factory import LazyAttribute
from faker import Faker
from factory import PostGenerationMethodCall, Sequence, LazyAttribute

from django.contrib.auth.models import User

PASSWORD = '1_test_TEST_!'
FAKE = Faker()


def generate_username() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=['username'])['username']


def generate_email() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=['mail'])['mail']


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    username = Sequence(lambda n: f'user{n}')
    email = 'test@localhost.com' # LazyAttribute(lambda obj: f'{obj.username)@localhost.com'
    password = PostGenerationMethodCall('set_password', PASSWORD)


