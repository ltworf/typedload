#!/usr/bin/python3

# typedload
# Copyright (C) 2020 Salvo "LtWorf" Tomaselli
#
# typedload is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

# This is a practical example on how to use the typedload library.

# Json data is downloaded from the internet and then loaded into
# Python data structures (dictionaries, lists, strings, and so on).

#This example queries github API

import argparse
from datetime import datetime
from enum import Enum
import json
from typing import *
import urllib.request

import typedload


class CommandLine(NamedTuple):
    full: bool
    project: Optional[str]
    username: Optional[str]

    def get_url(self) -> str:
        if self.username is None and self.project is None:
            username = 'ltworf'
            project = 'typedload'
        elif self.username and self.project:
            username = self.username
            project = self.project
        else:
            raise ValueError('Username and project need to be set together')
        return 'https://api.github.com/repos/%s/%s/releases' % (username, project)


class UserTypes(Enum):
    #FIXME I could not find the documentation of what the other values can be
    USER = 'User'


class AssetState(Enum):
    #FIXME I could not find the documentation of what the other values can be
    UPLOADED = 'uploaded'


class User(NamedTuple):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    received_events_url: str
    type: UserTypes
    site_admin: bool


class Asset(NamedTuple):
    url: str
    id: int
    node_id: str
    name: str
    uploader: User
    content_type: str
    state: AssetState
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    browser_download_url: str


class Release(NamedTuple):
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    author: User
    prerelease: bool
    created_at: datetime
    published_at: datetime
    assets: List[Asset]


def get_data(args: CommandLine) -> Any:
    """
    Use the github API to get releases information
    """
    req = urllib.request.Request(args.get_url())
    with urllib.request.urlopen(req) as f:
        return json.load(f)


def print_report(data: List[Release], args: CommandLine):
    for i in data:
        if i.draft or i.prerelease:
            continue
        print('Release:', i.name, end=' ')

        if args.full:
            print('Created by:', i.author.login, 'on:', i.created_at)
        else:
            print()

        for asset in i.assets:
            if asset.download_count or args.full:
                print('\t%d\t%s' % (asset.download_count, asset.name))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='The username to query')
    parser.add_argument('-p', '--project', help='The project to query')
    parser.add_argument('-f', '--full', help='Print the full report', action='store_true')

    # We load the args into a NamedTuple, so it is no longer an obscure dynamic object but it is typed
    args = typedload.load(parser.parse_args(), CommandLine)
    data = get_data(args)


    # Github returns dates like this "2016-08-23T18:26:00Z", which are not supported by typedload
    # So we make a custom handler for them.
    loader = typedload.dataloader.Loader()
    loader.handlers.insert(0, (# Make the new handler first so it overrides the current handler for datetime
        lambda t: t == datetime,
        lambda l, v, t: datetime.fromisoformat(v[:-1])
    ))


    # We know what the API returns so we can load the json into typed data
    typed_data = loader.load(data, List[Release])
    print_report(typed_data, args)


if __name__ == '__main__':
    main()
