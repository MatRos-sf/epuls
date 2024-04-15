from django.test import TestCase, tag

from account.factories import UserFactory
from account.models import Profile


# forms
@tag("fo_pf")
class PictureFormTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PictureFormTestCase, cls).setUpClass()
        UserFactory()

    def setUp(self):
        self.profile = Profile.objects.first()

    # TODO: I am not able to test image field
