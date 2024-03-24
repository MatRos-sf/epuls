from factory import SubFactory
from factory.django import DjangoModelFactory
from profile_factory import UserFactory

from account.models import Diary


class DiaryFactory(DjangoModelFactory):
    class Meta:
        model = Diary

    author = SubFactory(UserFactory)
    title = "Test Diary"
    content = "Test Content"
    is_hide = False
