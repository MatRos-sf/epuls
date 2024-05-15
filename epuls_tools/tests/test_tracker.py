from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.test import TestCase, tag

from account.factories import UserFactory
from epuls_tools.expections import TrackerUserNotFoundError
from epuls_tools.views.tracker import EpulsTracker
from photo.factories import GalleryFactory


@tag("t_t")
class EpulsTrackerTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        UserFactory()

    def setUp(self):
        self.user = User.objects.first()

    # test method -> get_user()
    def test_should_return_user_when_user_object_is_set(self):
        tracker = EpulsTracker()
        tracker.user_object = self.user

        self.assertEqual(tracker.get_user(), self.user)

    @patch("epuls_tools.views.tracker.EpulsTracker.capture_user")
    def test_should_return_user_when_capture_user_is_mock(self, mock_capture_user):
        mock_capture_user.return_value = self.user

        tracker = EpulsTracker()
        response = tracker.get_user()

        self.assertEqual(response, self.user, tracker.get_user())

    def test_should_trigger_custom_capture_user_method_when_user_subclasses(self):
        expected_user = UserFactory()

        class CustomEpulsTracker(EpulsTracker):
            def capture_user_new_method(self):
                return expected_user

        custom_class = CustomEpulsTracker()
        response = custom_class.get_user()

        self.assertEqual(response, expected_user)

    def test_should_capture_user_from_url_when_trigger_get_user(self):
        expected = UserFactory(username="test_user")

        tracker = EpulsTracker()
        tracker.kwargs = {"username": "test_user"}

        response = tracker.get_user()

        self.assertEqual(response, expected)

    def test_should_capture_user_when_object_has_user_field(self):
        tracker = EpulsTracker()
        tracker.object = self.user.profile

        expected = tracker.get_user()

        self.assertEqual(self.user, expected)

    def test_should_capture_user_when_object_has_field_profile(self):
        gallery = GalleryFactory(profile=self.user.profile)
        expected_user = gallery.profile.user

        tracker = EpulsTracker()
        tracker.object = gallery

        expected = tracker.get_user()

        self.assertEqual(expected_user, expected)

    def test_should_raise_custom_error_when_could_not_find_user_instance(self):
        tracker = EpulsTracker()
        with self.assertRaises(TrackerUserNotFoundError):
            tracker.get_user()

    # test method -> get_login_user()
    def test_should_return_login_user_when_currently_user_was_set(self):
        tracker = EpulsTracker()
        tracker.current_user = self.user

        response = tracker.get_login_user()

        self.assertEqual(response, self.user)

    def test_should_set_current_user(self):
        tracker = EpulsTracker()

        # create real User instance
        tracker.request = self.client.request().wsgi_request

        tracker.request.user = self.user

        expected = tracker.get_login_user()

        self.assertEqual(expected, self.user)

    def test_should_set_current_user_with_mock(self):
        tracker = EpulsTracker()

        # mock object
        tracker.request = Mock()
        tracker.request.user = self.user

        expected = tracker.get_login_user()

        self.assertEqual(expected, self.user)
