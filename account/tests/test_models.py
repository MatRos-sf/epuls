from datetime import datetime
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.forms import ValidationError
from django.test import TestCase, tag
from django.utils import timezone
from parameterized import parameterized

from account.factories import UserFactory
from account.models import TYPE_OF_PROFILE, AboutUser, Profile, ProfileType


@tag("p")
class ProfileModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfileModelTest, cls).setUpClass()
        UserFactory.create_batch(2)

    def setUp(self):
        self.profile = Profile.objects.first()

    # test properties
    def test_when_model_is_initialized_should_set_currently_type_to_basic(self):
        self.assertEquals(self.profile.currently_type, "B")

    def test_should_return_zero_when_cunt_visitor(self):
        self.assertEquals(self.profile.count_visitors, 0)

    @parameterized.expand([(0, 10, 10), (100, 100, 200)])
    def test_should_return_expected_value_of_visitor(self, male, female, expected):
        self.profile.male_visitor = male
        self.profile.female_visitor = female
        self.profile.save()

        self.assertEquals(self.profile.count_visitors, expected)

    def test_should_return_none_when_user_did_not_set_a_date_of_birth(self):
        self.assertIsNone(self.profile.date_of_birth)

    @parameterized.expand(
        [
            (datetime(2022, 3, 25), 2),
            (datetime(2022, 3, 26), 1),
            (datetime(2022, 3, 24), 2),
        ]
    )
    @patch("django.utils.timezone.now")
    def test_should_return_expected_age(self, dob, expected, mock_now):
        mock_now.return_value = timezone.make_aware(
            datetime(year=2024, month=3, day=25)
        )

        self.profile.date_of_birth = timezone.make_aware(dob)
        self.profile.save()

        self.assertEquals(self.profile.age, expected)

    # test methods
    @parameterized.expand([("B", 2, 1), ("X", 2, 1), ("P", 2, 1), ("D", 2, 1)])
    def test_should_return_true_when_user_can_permitted_to_add_picture(
        self, type_of_profile, max_value, size
    ):
        with patch.dict("account.models.TYPE_OF_PROFILE", clear=False) as top:
            top[type_of_profile] = {"picture": max_value}

            self.assertTrue(self.profile.is_image_permitted(size))

    @parameterized.expand(
        [
            ("B", 1, 2),
        ]
    )
    def test_should_return_false_when_user_cannot_add_picture(
        self, type_of_profile, max_value, size
    ):
        with patch.dict("account.models.TYPE_OF_PROFILE", clear=False) as top:
            top[type_of_profile] = {"picture": max_value}

            self.assertFalse(self.profile.is_image_permitted(size))

    @parameterized.expand(
        [
            (ProfileType.BASIC, 60),
            (ProfileType.PRO, 80),
            (ProfileType.XTREME, 130),
            (ProfileType.DIVINE, 200),
        ]
    )
    def test_should_return_friend_limit(self, type_of_profile, max_friends):
        self.profile.type_of_profile = type_of_profile
        self.profile.save()
        self.assertEquals(self.profile.pull_field_limit("friends"), max_friends)

    def test_should_add_friends(self):
        second_profile = Profile.objects.last()
        self.profile.add_friend(second_profile.user)

        self.assertEquals(self.profile.friends.count(), 1)

    @parameterized.expand(
        [ProfileType.BASIC, ProfileType.PRO, ProfileType.DIVINE, ProfileType.XTREME]
    )
    def test_should_not_add_friends_when_user_have_amt_friends_eq_acceptable_amt(
        self, type_of_profile
    ):
        # change type of profile
        self.profile.type_of_profile = type_of_profile
        self.profile.save()

        with patch("account.models.Profile.friends") as mock_friends:
            mock_friends.count.return_value = TYPE_OF_PROFILE[type_of_profile][
                "friends"
            ]

            with self.assertRaises(ValidationError):
                self.profile.add_friend(User.objects.last())

    @parameterized.expand(
        [ProfileType.BASIC, ProfileType.PRO, ProfileType.DIVINE, ProfileType.XTREME]
    )
    def test_should_add_friends_when_user_have_amt_friends_eq_extreme_num(
        self, type_of_profile
    ):
        # change type of profile
        self.profile.type_of_profile = type_of_profile
        self.profile.save()

        with patch("account.models.Profile.friends") as mock_friends:
            mock_friends.count.return_value = (
                TYPE_OF_PROFILE[type_of_profile]["friends"] - 1
            )

            self.profile.add_friend(User.objects.last())

    def test_should_do_nothing_when_user_try_delete_friend_but_user_does_not_any_friends(
        self,
    ):
        self.assertEquals(self.profile.friends.count(), 0)
        user_to_del = User.objects.last()

        self.profile.remove_friend(user_to_del)
        self.assertEquals(self.profile.friends.count(), 0)

    def test_should_not_add_to_friends_when_user_try_add_yourself(self):
        user_to_add = self.profile.user

        self.profile.add_friend(user_to_add)

        self.assertEquals(self.profile.friends.count(), 0)

    def test_should_remove_friends_when_user_try_remove_one_of_them(self):
        from random import choice

        users = UserFactory.create_batch(3)

        self.profile.friends.add(*users)
        self.profile.save()

        # remove random one
        user_to_remover = choice(users)
        self.profile.friends.remove(user_to_remover)

        self.assertEquals(self.profile.friends.count(), 2)

    def test_should_not_allow_add_bf_when_user_has_basic_account(self):
        bf = User.objects.last()

        with self.assertRaises(ValidationError) as ve:
            self.profile.add_best_friend(bf)

        self.assertEquals(
            ve.exception.messages[0],
            "You cannot add best friend because you have a basic account!",
        )

    def test_should_not_add_bf_when_user_try_add_yourself(self):
        self.profile.type_of_profile = ProfileType.XTREME
        self.profile.save()

        bf = self.profile.user

        with self.assertRaises(ValidationError) as ve:
            self.profile.add_best_friend(bf)

        self.assertEquals(
            ve.exception.messages[0],
            "You cannot add best friend if friend is not in your friends list or you are the best friend",
        )

    def test_should_not_add_bf_when_user_is_not_in_friend_list(self):
        user = User.objects.last()

        self.profile.type_of_profile = ProfileType.XTREME

        with self.assertRaises(ValidationError) as ve:
            self.profile.add_best_friend(user)

        self.assertEquals(
            ve.exception.messages[0],
            "You cannot add best friend if friend is not in your friends list or you are the best friend",
        )

    @parameterized.expand([ProfileType.XTREME, ProfileType.PRO, ProfileType.DIVINE])
    def test_should_add_bf_when_user_suit_requirements(self, type_of_profile):
        user = UserFactory()

        self.profile.friends.add(user)
        self.profile.type_of_profile = type_of_profile
        self.profile.save()

        self.profile.add_best_friend(user)

        self.assertEquals(self.profile.best_friends.count(), 1)

    @parameterized.expand([ProfileType.PRO, ProfileType.DIVINE, ProfileType.XTREME])
    def test_should_add_bf_when_user_have_amt_friends_eq_extreme_num(
        self, type_of_profile
    ):
        users = UserFactory.create_batch(2)

        self.profile.friends.add(*users)
        self.profile.type_of_profile = type_of_profile
        self.profile.save()

        max_num_of_bf = TYPE_OF_PROFILE[type_of_profile]["best_friends"]
        with patch("account.models.Profile.best_friends") as mock_bf:
            mock_bf.count.return_value = max_num_of_bf - 2

            for user in users:
                self.profile.add_best_friend(user)
