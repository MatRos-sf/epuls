from django.test import TestCase

from account.factories import UserFactory


class SimpleDBTestCase(TestCase):
    """
    Test creates a simple database:
        * 6 users
        * only first user has 5 friends
    """

    @classmethod
    def setUpClass(cls):
        super(SimpleDBTestCase, cls).setUpClass()
        users = UserFactory.create_batch(6)
        main_user = users[0]

        for user in users[1:]:
            main_user.profile.friends.add(user)
