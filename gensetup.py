#!/usr/bin/python3

# typedload
# Copyright (C) 2018-2023 Salvo "LtWorf" Tomaselli
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

from sys import argv, exit

def load_version():
    with open('CHANGELOG', 'rt') as f:
        return f.readline().strip()

AUTHOR = 'Salvo \'LtWorf\' Tomaselli'
AUTHOR_EMAIL = 'tiposchi@tiscali.it'
URL = 'https://ltworf.github.io/typedload/'
BUGTRACKER = 'https://github.com/ltworf/typedload/issues'
DESCRIPTION = 'Load and dump data from json-like format into typed data structures'
KEYWORDS='typing types mypy json schema json-schema python3 namedtuple enums dataclass pydantic'
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Typing :: Typed',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
]

if len(argv) != 2:
    exit('Wrong command line')

if argv[1] == '--setup.py':
    with open('setup.py', 'wt') as f:
        print(
f'''#!/usr/bin/python3
# This file is auto generated. Do not modify
from setuptools import setup
setup(
    name='typedload',
    version={load_version()!r},
    description='{DESCRIPTION}',
    readme='README.md',
    url='{URL}',
    author={AUTHOR!r},
    author_email='{AUTHOR_EMAIL}',
    license='GPL-3.0-only',
    classifiers={CLASSIFIERS!r},
    keywords='{KEYWORDS}',
    packages=['typedload'],
    package_data={{"typedload": ["py.typed", "__init__.pyi"]}},
)''', file=f
    )

elif argv[1] == '--pyproject.toml':
    with open('pyproject.toml', 'wt') as f:
        print(
f'''[project]
name = "typedload"
version = "{load_version()}"
authors = [
  {{ name="{AUTHOR}", email="{AUTHOR_EMAIL}" }},
]
description = "{DESCRIPTION}"
readme = "README.md"
requires-python = ">=3.8"
classifiers = {CLASSIFIERS!r}
keywords = {KEYWORDS.split(' ')!r}
license = {{file = "LICENSE"}}

[project.urls]
"Homepage" = "{URL}"
"Bug Tracker" = "{BUGTRACKER}"

[build-system]
requires = ["setuptools", "wheel"]
''', file=f
        )
