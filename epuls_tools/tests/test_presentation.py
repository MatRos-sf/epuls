import os
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.base import File
from django.test import TestCase, tag
from parameterized import parameterized
from PIL import Image

from account.factories import UserFactory
from account.models import Profile
from epuls_tools.presentation import (
    Component,
    ProfilePictureComponent,
    Tag,
    UserComponent,
)


def generate_photo_file(name="test"):
    name = name if name.endswith(".jpg") else name + ".jpg"
    file_obj = BytesIO()
    color = (256, 0, 0)
    image = Image.new("RGB", size=(200, 200), color=color)
    image.save(file_obj, format="JPEG")

    file_obj.seek(0)

    return File(file_obj, name=name)


@tag("1")
class ComponentTestCase(TestCase):
    def setUp(self):
        self.component = Component()

    @parameterized.expand(["", "test", "tes t"])
    def test_should_find_everything(self, html):
        self.component.find(html)

        self.assertFalse(self.component.tags)

    @parameterized.expand(["<a href=@user1>John</a>", "<p>No tags here</p>"])
    def tes_should_return_the_same_html(self, html):
        response = self.component.link(html)
        self.assertEqual(html, response)


@tag("ep_p_uc")
class UserComponentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(UserComponentTestCase, cls).setUpClass()
        UserFactory(username="Test")

    def setUp(self):
        self.dummy_presentation = """"
        # pass
        <a href=@Test ></a>
        <a href=@Test  ></a>
        <a href=@Test    ></a>
        <a href=@Test class=\"test\" ></a>

        #fail
        a href=@Test ></a>
        <a href=@Test ></a
        <a href=@Test > </a>
        <href=@Test ></a>
        <a class=@Test href=@Test></a>
        <a class=@Test ></a>
        """

        self.component = UserComponent()

    def test_should_find_four_tags(self):
        self.component.find(self.dummy_presentation)
        self.assertEqual(len(self.component.tags), 4)

    def test_should_create_appropriate_tags(self):
        expected_list = [
            Tag(tag="<a href=@Test ></a>", username="Test", extra_property="", url=""),
            Tag(tag="<a href=@Test  ></a>", username="Test", extra_property="", url=""),
            Tag(
                tag="<a href=@Test    ></a>", username="Test", extra_property="", url=""
            ),
            Tag(
                tag='<a href=@Test class="test" ></a>',
                username="Test",
                extra_property='class="test"',
                url="",
            ),
        ]
        self.component.find(self.dummy_presentation)

        tags = self.component.tags

        self.assertListEqual(expected_list, tags)

    def test_should_edit_html_and_replace_correctly_tag_to_new_one(self):
        tags = [
            Tag(tag="<a href=@Test ></a>", username="Test", extra_property="", url=""),
            Tag(tag="<a href=@Test  ></a>", username="Test", extra_property="", url=""),
            Tag(
                tag="<a href=@Test    ></a>", username="Test", extra_property="", url=""
            ),
            Tag(
                tag='<a href=@Test class="test" ></a>',
                username="Test",
                extra_property='class="test"',
                url="",
            ),
        ]
        self.component.tags = tags
        html = (
            "<a href=@Test ></a> "
            "<a href=@Test  ></a> "
            "<a href=@Test    ></a> "
            '<a href=@Test class="test" ></a> '
        )

        result = self.component.sub(html)

        expected = (
            '<a href="/Test/" >Test</a> '
            '<a href="/Test/" >Test</a> '
            '<a href="/Test/" >Test</a> '
            '<a href="/Test/" class="test">Test</a> '
        )

        self.assertEqual(result, expected)


@tag("ep_p_ppc")
class ProfilePictureComponentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProfilePictureComponentTestCase, cls).setUpClass()
        users = UserFactory.create_batch(2)
        for user in users:
            user.profile.profile_picture = generate_photo_file()
            user.profile.save()
        UserFactory()

    @classmethod
    def tearDownClass(cls):
        files_to_del = [
            p.profile_picture.path for p in Profile.objects.all() if p.profile_picture
        ]

        for path in files_to_del:
            if os.path.exists(path):
                os.remove(path)

        super(ProfilePictureComponentTestCase, cls).tearDownClass()

    def setUp(self):
        self.profile = Profile.objects.first()

        self.dummy_presentation = """
        <img src=@prof-Test >
        <img src=@prof-Test    >
        <img src=@prof-Test class="Test" >
        """

    def test_should_create_three_tags(self):
        component = ProfilePictureComponent()

        component.find(self.dummy_presentation)

        self.assertEqual(len(component.tags), 3)

    @parameterized.expand(
        [
            "<img src=@prof-_ala >",
            "<img src=@prof-la@la >",
            "<img src=@prof-@@@la12_31aS >",
        ]
    )
    def test_should_create_find_tags(self, html):
        component = ProfilePictureComponent()

        component.find(html)

        self.assertEqual(len(component.tags), 1)

    @parameterized.expand(
        [
            "<img src=@prof-!ala >",
            "<img src=@prof- >",
            "<img class='test' src=@prof-@@@la12_31aS >",
        ]
    )
    def test_should_not_create_tags(self, html):
        component = ProfilePictureComponent()

        component.find(html)

        self.assertEqual(len(component.tags), 0)

    def test_should_return_expected_dict_when_trigger_pull_url_profile_picture(self):
        # mock tags
        user1, user2, user3 = User.objects.all()
        tags = [
            Tag(tag="...", username=user1.username, extra_property="", url=""),
            Tag(tag="...", username=user2.username, extra_property="", url=""),
            Tag(tag="...", username=user3.username, extra_property="", url=""),
        ]

        # create expected dict
        expected = {
            user1.username: user1.profile.profile_picture.url,
            user2.username: user2.profile.profile_picture.url,
            user3.username: f"/static/account/profile_picture/default_{user3.profile.gender}_picture.jpeg",
        }

        component = ProfilePictureComponent()

        component.tags = tags

        result = component.pull_url_profile_picture()

        self.assertEqual(result, expected)
