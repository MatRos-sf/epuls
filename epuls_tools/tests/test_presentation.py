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
    PictureComponent,
    Presentation,
    ProfilePictureComponent,
    Tag,
    UserComponent,
)
from photo.factories import GalleryFactory, PictureFactory
from photo.models import Picture


def generate_photo_file(name="test"):
    name = name if name.endswith(".jpg") else name + ".jpg"
    file_obj = BytesIO()
    color = (256, 0, 0)
    image = Image.new("RGB", size=(200, 200), color=color)
    image.save(file_obj, format="JPEG")

    file_obj.seek(0)

    return File(file_obj, name=name)


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

        result = component.pull_url_picture()

        self.assertEqual(result, expected)

    def test_should_return_expected_html_and_update_tags(self):
        username = self.profile.user.username
        html = f"<img src=@prof-{username} >"

        component = ProfilePictureComponent()
        response = component.link(html)

        expected = f'<a href="/{username}/"><img src="/media/{self.profile.profile_picture}" ></a>'

        self.assertEqual(response, expected)


@tag("pctc")
class PictureComponentTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PictureComponentTestCase, cls).setUpClass()
        user = UserFactory()
        gallery = GalleryFactory(profile=user.profile)
        PictureFactory.create_batch(3, profile=user.profile, gallery=gallery)

    @classmethod
    def tearDownClass(cls):
        url_pictures_to_del = [
            picture.picture.path for picture in Picture.objects.all()
        ]

        for path in url_pictures_to_del:
            if os.path.exists(path):
                os.remove(path)

        super(PictureComponentTestCase, cls).tearDownClass()

    def setUp(self):
        for index, picture in enumerate(Picture.objects.all()):
            setattr(self, f"picture_{index}", picture)
        self.user = User.objects.first()

    def test_should_create_src_when_pattern_is_correct(self):
        html = f"<img src=@img-{self.picture_1.presentation_tag} > "
        component = PictureComponent(self.user.profile)

        response = component.link(html)

        self.assertEqual(f'<img src="/media/{self.picture_1.picture}" > ', response)

    def test_user_can_not_mention_about_different_user_picture(self):
        new_user = UserFactory()
        gallery = GalleryFactory(profile=new_user.profile)
        picture = PictureFactory(profile=new_user.profile, gallery=gallery)

        html = f"<img src=@img-{picture.presentation_tag} >"

        component = PictureComponent(self.user.profile)

        response = component.link(html)
        self.assertEqual(response, '<img src="" >')


@tag("p_ts")
class PresentationTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PresentationTestCase, cls).setUpClass()
        user = UserFactory()
        user.profile.profile_picture = generate_photo_file()
        user.profile.save()

        gallery = GalleryFactory(profile=user.profile)
        PictureFactory.create_batch(3, profile=user.profile, gallery=gallery)

    @classmethod
    def tearDownClass(cls):
        url_pictures_to_del = [
            picture.picture.path for picture in Picture.objects.all()
        ]

        for path in url_pictures_to_del:
            if os.path.exists(path):
                os.remove(path)

        super(PresentationTestCase, cls).tearDownClass()

    def setUp(self):
        self.user = User.objects.first()

    def test_should_delete_unwanted_src(self):
        html = (
            '<img src="test.js" > '
            '<img src="test.js" class="sth" > '
            '<img src="www.test.com" > '
            '<a src="test.js" > '
            '<a src="test.js" class="sth" > '
            '<a src="www.test.com" ></a>'
            ' <iframe src="https://www.test.com"></iframe> '
        )

        presentation = Presentation(html, self.user.profile)
        presentation.check_html()

        self.assertEqual(
            presentation.html,
            (
                '<img src="" > '
                '<img src="" class="sth" > '
                '<img src="" > '
                '<a src="" > '
                '<a src="" class="sth" > '
                '<a src="" ></a>'
                ' <iframe src=""></iframe> '
            ),
        )
