"""
     Factory for:
        - User model
        - Profile model
        - Visitor model
        - FriendRequest model
"""
from django.contrib.auth.models import User
from factory import (
    LazyAttribute,
    PostGenerationMethodCall,
    Sequence,
    SubFactory,
    post_generation,
)
from factory.django import DjangoModelFactory
from faker import Faker

from account.models import FriendRequest, Profile, Visitor

PASSWORD = "1_test_TEST_!"
FAKE = Faker()

# TODO factory: about_me, puls


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Sequence(lambda n: f"user{n}")
    email = LazyAttribute(lambda _: FAKE.unique.email())
    password = PostGenerationMethodCall("set_password", PASSWORD)


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = SubFactory(UserFactory)
    about_me = SubFactory(...)
    puls = SubFactory(...)

    @post_generation
    def friends(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.friends.add(*extracted)

    @post_generation
    def best_friends(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.best_friends.add(*extracted)


class VisitorFactory(DjangoModelFactory):
    visitor = SubFactory(UserFactory)
    receiver = SubFactory(UserFactory)

    class Meta:
        model = Visitor


class FriendRequestFactory(DjangoModelFactory):
    class Meta:
        model = FriendRequest

    from_user = SubFactory(UserFactory)
    to_user = SubFactory(UserFactory)
