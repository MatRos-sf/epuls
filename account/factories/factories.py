from factory import SubFactory
from factory.django import DjangoModelFactory

from account.models import Diary

from .profile_factory import UserFactory


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = "Test Diary"
    content = "Test Content"
    is_hide = False
