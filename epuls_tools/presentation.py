import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import partial
from typing import List, Optional, Tuple

from django.shortcuts import reverse

from account.models import Profile


class BasicComponent(ABC):
    @abstractmethod
    def sub(self, html) -> str:
        pass

    @abstractmethod
    def find(self, html) -> None:
        pass

    @abstractmethod
    def link(self, html) -> str:
        pass


@dataclass
class Tag:
    tag: str
    username: str
    extra_property: str = ""
    url: str = ""


class UserComponent(BasicComponent):
    def __init__(self):
        self.pattern = re.compile(r"<a href=@(\w+) (.*)></a>")
        self.template = '<a href="{url}" {extra_property} >{username}</a>'
        self.endpoint = partial(reverse, "account:profile")

        self.tags = []

    def sub(self, html: str) -> str:
        for tag in self.tags:
            url = reverse("account:profile", kwargs={"username": tag.username})
            html = html.replace(
                tag.tag,
                self.template.format(
                    username=tag.username, url=url, extra_property=tag.extra_property
                ),
            )

        return html

    def find(self, html) -> List[Tag]:
        matches = self.pattern.finditer(html)
        for match in matches:
            username, extra_property = match.groups()
            tag = Tag(
                tag=match.group(), username=username, extra_property=extra_property
            )
            self.tags.append(tag)

    def link(self, html):
        self.find(html)

        if not self.tags:
            return html

        return self.sub(html)


class ProfilePictureComponent(BasicComponent):
    def __init__(self):
        self.pattern = re.compile(r"<img src=@prof-(\w+) (.*)>")
        self.template = (
            '<a href="{url_user}" ><img src="{url_img}" {extra_property} ></a>'
        )
        self.endpoint = partial(reverse, "account:profile")

        self.tags = []

    def sub(self, html: str) -> str:
        for tag in self.tags:
            html = html.replace(
                tag.tag,
                self.template.format(
                    extra_property=tag.extra_property,
                    url_user=reverse(
                        "account:profile", kwargs={"username": tag.username}
                    ),
                    url_img=tag.url,
                ),
            )

        return html

    def find(self, html):
        matches = self.pattern.finditer(html)
        for match in matches:
            username, extra_property = match.groups()
            tag = Tag(
                tag=match.group(), username=username, extra_property=extra_property
            )
            self.tags.append(tag)

    def update_tags(self, values):
        for tag in self.tags:
            if values.get(tag.username, None):
                tag.url = values.get(tag.username)

    def get_default_profile_picture(self, gender):
        return f"/static/account/profile_picture/default_{gender}_picture.jpeg"

    def get_user_url_picture(self, users):
        """

        :param users: List
        :return: Dict[str, str]
        """

        users_dataset = Profile.objects.filter(user__username__in=users).values(
            "user__username", "profile_picture", "gender"
        )

        info_about_users = {}

        for dataset in users_dataset:
            username = dataset.pop("user__username")
            profile_picture = dataset.pop("profile_picture")

            if not profile_picture:
                gender = dataset.pop("gender")
                profile_picture = self.get_default_profile_picture(gender)
            else:
                profile_picture = "/media/" + profile_picture
            info_about_users[username] = profile_picture

        return info_about_users

    def link(self, html):
        self.find(html)
        if not self.tags:
            return html

        # get users
        users = [tag.username for tag in self.tags]

        # get information about users

        url_pictures = self.get_user_url_picture(users)
        self.update_tags(url_pictures)

        return self.sub(html)


class Presentation:
    def __init__(self, html):
        self.user_component = UserComponent()
        self.profile_picture = ProfilePictureComponent()

        self.html = html

    def convert(self):
        self.html = self.user_component.link(self.html)
        self.html = self.profile_picture.link(self.html)
        return self.html
