#!/usr/bin/env python
import os
from github3 import login

from assembla import API

GITHUB_USER = os.environ.get("GITHUB_USER", "")
GITHUB_PASS = os.environ.get("GITHUB_PASS", "")

ASSEMBLA_KEY = os.environ.get("ASSEMBLA_KEY", "")
ASSEMBLA_SECRET = os.environ.get("ASSEMBLA_SECRET", "")
ASSEMBLA_SPACE = os.environ.get("ASSEMBLA_SPACE", "")

GITHUB_AUTHOR = os.environ.get("GITHUB_AUTHOR", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")

gh = login(GITHUB_USER, password=GITHUB_PASS)

assembla = API(
    key=ASSEMBLA_KEY,
    secret=ASSEMBLA_SECRET,
)


def get_user_info(gh, my_space):
    """
    Use this to help you extract the github users and assembla users, so you can setup the usermap
    """
    users = my_space.users()
    for user in users:
        print user['id'], user['login']

    repo = gh.repository(GITHUB_AUTHOR, GITHUB_REPO)
    for user in repo.iter_assignees():
        print user.login


if __name__ == "__main__":

    my_space = assembla.spaces(name=ASSEMBLA_SPACE)[0]
    get_user_info(gh, my_space)
