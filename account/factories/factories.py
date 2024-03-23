from factory import SubFactory
from factory.django import DjangoModelFactory
from faker import Faker
from profile_factory import UserFactory

from account.models import Diary

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


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = "Test Diary"
    content = "Test Content"
    is_hide = False
