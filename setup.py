#!/usr/bin/python3

# typedload
# Copyright (C) 2018-2021 Salvo "LtWorf" Tomaselli
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

with open('README.md', 'rt') as f:
    long_description = ''.join((i for i in  f.readlines() if not i.startswith('![')))

setup(
    name='typedload',
    version='2.10',
    description='Load and dump data from json-like format into typed data structures',
    long_description_content_type='text/markdown',
    long_description=long_description,
    url='https://ltworf.github.io/typedload/',
    author='Salvo \'LtWorf\' Tomaselli',
    author_email='tiposchi@tiscali.it',
    license='GPLv3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='typing types mypy json',
    packages=['typedload'],
    package_data={"typedload": ["py.typed"]},
)
