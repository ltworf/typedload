#!/usr/bin/python3

# typedload
# Copyright (C) 2018-2019 Salvo "LtWorf" Tomaselli
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

from distutils.core import setup

setup(
    name='typedload',
    version='1.16',
    description='Load and dump data from json-like format into typed data structures',
    long_description='''Load and dump json-like data into typed data structures.

This module provides an API to load dictionaries and lists (usually loaded
from json) into Python's NamedTuples, dataclass, sets, enums, and various
other typed data structures; respecting all the type-hints and performing
type checks or casts when needed.

It can also dump from typed data structures to json-like dictionaries and lists.

It is very useful for projects that use Mypy and deal with untyped data
like json, because it guarantees that the data will have the expected format.
''',
    url='https://github.com/ltworf/typedload',
    author='Salvo \'LtWorf\' Tomaselli',
    author_email='tiposchi@tiscali.it',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='typing types mypy json',
    packages=['typedload', 'typedload.plugins'],
    package_data={"typedload": ["py.typed"]},
)
