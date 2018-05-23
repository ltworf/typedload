#!/usr/bin/python3

# typedload
# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
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
    version='1.4',
    description='Load and dump data from json-like format into typed data structures',
    long_description='''Manipulating data loaded from json is very error prone.

If the format changes unexpectedly, errors arise at the time of use, fields can
disappear or change type.

This library allows loading data using NamedTuple and similar type hints,
to obtain a more safe to use data structure. All exceptions will be generated in
a single point, when loading, rather than in multiple points, when using.

It also provides a module to do the opposite and revert back to something that
can be converted to json.
''',
    url='https://github.com/ltworf/typedload',
    author='Salvo \'LtWorf\' Tomaselli',
    author_email='tiposchi@tiscali.it',
    license='GPLv3',
    classifiers=[
       # 'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='typing types mypy json',
    packages=['typedload', 'typedload.plugins'],
    package_data={"typedload": ["py.typed"]},
)
