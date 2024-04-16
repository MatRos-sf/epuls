import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import Dict, List, NamedTuple, Optional, Tuple

from django.shortcuts import reverse

from account.models import Profile
from photo.models import Picture


@dataclass
class Tag:
    tag: str
    username: str
    extra_property: str
    url: str = ""


class BasicComponent(ABC):
    @abstractmethod
    def sub(self, html: str) -> str:
        """
        This method replaces old tags with new ones.
        Don't forget to implement the 'tags' attribute.
        """
        pass

    def find(self, html) -> None:
        """
        This method should find all tags according to self._pattern and sets all of them in self.tags.
        """
        pass

    @abstractmethod
    def link(self, html) -> str:
        """
        This method combines the other two methods, find and sub, and returns a new HTML string.
        """
        pass


class Component:
    _pattern = re.compile(".")
    _template = ""

    def __init__(self):
        self.endpoint = None
        self.tags = []

    def find(self, html: str) -> None:
        """
        Finds all tags according to self._pattern using regular expressions and sets them in self.tags.
        """
        matches = self._pattern.finditer(html)
        for match in matches:
            groups = match.groups()
            if len(groups) < 2:
                continue

            username, extra_property = groups
            tag = Tag(
                tag=match.group(),
                username=username,
                extra_property=extra_property.replace(" ", ""),
                url="",
            )
            self.tags.append(tag)

    def sub(self, html: str) -> str:
        """
        Replaces old tags in HTML code with new ones based on user data.
        """
        for tag in self.tags:
            html = html.replace(tag.tag, self._build_replacement(tag))
        return html

    def link(self, html: str) -> str:
        """
        Combines the sub and find methods to return modified HTML code if the pattern is matched.
        Returns the original HTML if no pattern is matched.
        """
        self.find(html)
        if not self.tags:
            return html
        return self.sub(html)

    def _build_replacement(self, tag: Tag) -> str:
        raise NotImplementedError


class UserComponent(Component):
    """The class is responsible for changing HTML when it mentions users."""

    _pattern = re.compile(r"<a href=@([a-zA-Z0-9@/./+/-/_]+) (.*)></a>")
    _template = '<a href="{url}" {extra_property}>{username}</a>'

    def __init__(self):
        super().__init__()
        self.endpoint = partial(reverse, "account:profile")

    def _build_replacement(self, tag: Tag) -> str:
        url = reverse("account:profile", kwargs={"username": tag.username})
        return self._template.format(
            username=tag.username, url=url, extra_property=tag.extra_property
        )


class ProfilePictureComponent(Component):
    """
    The class is responsible for changing HTML when it mentions users profile photo.
    """

    _pattern = re.compile(r"<img src=@prof-([a-zA-Z0-9@/./+/-/_]+) (.*)>")
    _template = '<a href="{url_user}"><img src="{url_img}" {extra_property}></a>'

    def __init__(self):
        super().__init__()
        self.endpoint = partial(reverse, "account:profile")

    def _build_replacement(self, tag: Tag) -> str:
        url_user = reverse("account:profile", kwargs={"username": tag.username})
        return self._template.format(
            extra_property=tag.extra_property, url_user=url_user, url_img=tag.url
        )

    def update_tags(self, values: Dict[str, str]) -> None:
        for tag in self.tags:
            tag.url = values.get(tag.username, "")

    def pull_url_picture(self) -> Dict[str, str]:
        """
        This method sends a request to the database to retrieve information about users' profile picture.
        If user does not have a profile picture, it triggers the method self.get_default_profile_picture to generate a default URL.
        Returns a dictionary mapping usernames to profile picture URLs.
        """
        users = [tag.username for tag in self.tags]
        users_dataset = Profile.objects.filter(user__username__in=users).values(
            "user__username", "profile_picture", "gender"
        )
        profile_pictures = {}
        for dataset in users_dataset:
            username = dataset.pop("user__username")
            profile_picture = dataset.pop("profile_picture")
            if not profile_picture:
                gender = dataset.pop("gender")
                profile_picture = self.get_default_profile_picture(gender)
            else:
                profile_picture = "/media/" + profile_picture
            profile_pictures[username] = profile_picture
        return profile_pictures

    @staticmethod
    def get_default_profile_picture(gender: str) -> str:
        return f"/static/account/profile_picture/default_{gender}_picture.jpeg"

    def link(self, html: str) -> str:
        self.find(html)
        if not self.tags:
            return html
        url_pictures = self.pull_url_picture()
        self.update_tags(url_pictures)
        return self.sub(html)


class PictureComponent(ProfilePictureComponent):
    _pattern = re.compile(r"<img src=@img-([a-zA-Z0-9@/./+/-/_]+) (.*)>")
    _template = '<img src="{url_img}" {extra_property}>'

    def __init__(self, user_profile: Profile):
        super().__init__()
        self.profile = user_profile

    def pull_url_picture(self) -> Dict[str, str]:
        title_pictures = [tag.username for tag in self.tags]

        pictures = Picture.objects.filter(
            profile=self.profile, presentation_tag__in=title_pictures
        ).values("presentation_tag", "picture")

        pictures_url = {}

        for dataset in pictures:
            tag = dataset.get("presentation_tag")
            pictures_url[tag] = dataset.get("picture")

        return pictures_url

    def _build_replacement(self, tag: Tag) -> str:
        return self._template.format(extra_property=tag.extra_property, url_img=tag.url)


class Presentation:
    def __init__(self, html: str, profile: Profile):
        self.user_component = UserComponent()
        self.profile_picture = ProfilePictureComponent()
        self.picture = PictureComponent(profile)

        self.html = html

    def check_html(self) -> None:
        """
        Search for unwanted 'src' attributes in the HTML code and replace them with an empty string.

        This is useful for sanitizing HTML code and remove potentially harmful or unwanted sources from image or script tags
        """
        pattern = re.compile(r"\ssrc\s*=\s*[\"\']\S+[\"\'](?=[\s>])")
        self.html = pattern.sub(' src=""', self.html)

    def convert(self) -> str:
        self.check_html()

        for func in [self.user_component, self.profile_picture, self.picture]:
            self.html = func.link(self.html)

        return self.html
