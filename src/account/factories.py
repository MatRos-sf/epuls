from django.contrib.auth.models import User
from factory import PostGenerationMethodCall, Sequence, SubFactory
from factory.django import DjangoModelFactory
from faker import Faker

from .models import Diary

PASSWORD = "1_test_TEST_!"
FAKE = Faker()


def generate_username() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=["username"])["username"]


def generate_email() -> str:
    """
    Returns a random username
    """
    return FAKE.profile(fields=["mail"])["mail"]


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user{n}")
    email = "test@localhost.com"  # LazyAttribute(lambda obj: f'{obj.username)@localhost.com'
    password = PostGenerationMethodCall("set_password", PASSWORD)


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = "Test Diary"
    content = "Test Content"
    is_hide = False
