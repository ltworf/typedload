#!/usr/bin/python3

# typedload
# Copyright (C) 2018-2022 Salvo "LtWorf" Tomaselli
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

def load_long_description():

    with open('README.md', 'rt') as f:
        long_description = [i for i in  f.readlines() if not i.startswith('![')]

    # Add double ===
    to_add = []
    for i, line in enumerate(long_description):
        line = line.rstrip()
        if set(line) != {'='}:
            continue # Line is not made of ======
        to_add.append((i, len(line)))

    to_add.reverse()
    for line, size in to_add:
        long_description.insert(line - 1, '=' * size + '\n')

    # Convert ``` to indentation
    indent_block = False
    for i in range(len(long_description)):
        line = long_description[i]
        if line.startswith('```'):
            indent_block = not indent_block
            long_description[i] = '\n>>>\n' if indent_block else '\n'
            continue

        if line.rstrip() == '' and indent_block:
            long_description[i] = '>>>\n'

    #for i, line in enumerate(long_description):
        #if not line.endswith('\n'):
            #print(i, 'AAAAAAAAAAAAAAAAAAAAA ERRORE!!!!')
        #print (i, line.rstrip())

    #from docutils import core
    #core.publish_string(''.join(long_description ))
    return long_description


def load_version():
    with open('CHANGELOG', 'rt') as f:
        return f.readline().strip()

AUTHOR = 'Salvo \'LtWorf\' Tomaselli'
AUTHOR_EMAIL = 'tiposchi@tiscali.it'
URL = 'https://ltworf.github.io/typedload/'
BUGTRACKER = 'https://github.com/ltworf/typedload/issues'
DESCRIPTION = 'Load and dump data from json-like format into typed data structures'
KEYWORDS='typing types mypy json'
CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Typing :: Typed',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
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
    long_description={''.join(load_long_description())!r},
    url='{URL}',
    author={AUTHOR!r},
    author_email='{AUTHOR_EMAIL}',
    license='GPLv3',
    classifiers={CLASSIFIERS!r},
    keywords='{KEYWORDS}',
    packages=['typedload'],
    package_data={{"typedload": ["py.typed", "__init__.pyi"]}},
)''', file=f
    )

elif argv[1] == '--pyproject.toml':
    with open('pyproject.toml', 'wt') as f:
        print(
f'''
[project]
name = "typedload"
version = "{load_version()!r}"
authors = [
  {{ name="{AUTHOR}", email="{AUTHOR_EMAIL}" }},
]
description = "{DESCRIPTION}"
readme = "README.md"
requires-python = ">=3.5"
classifiers = {CLASSIFIERS!r}
keywords = "{KEYWORDS}"

[project.urls]
"Homepage" = "{URL}"
"Bug Tracker" = "{BUGTRACKER}"

[build-system]
requires = ["setuptools", "wheel"]
''', file=f
        )
