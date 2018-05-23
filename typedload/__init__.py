# typedload
#
# This library loads Python data structures into
# more strict data structures.
#
# The main purpose is to load things that come from
# json, bson or similar into NamedTuple.
#
# For example this Json:
#    {
#        'users': [
#            {
#                'username': 'salvo',
#                'shell': 'bash',
#                'sessions': ['pts/4', 'tty7', 'pts/6']
#            },
#            {
#                'username': 'lop'
#            }
#        ],
#    }
#
# Can be treated more easily if loaded into this:
#
#class User(NamedTuple):
#    username: str
#    shell: str = 'bash'
#    sessions: List[str] = []
#
#class Logins(NamedTuple):
#    users: List[User]
#
# And can then be loaded with
#
# typedload.load(data, Logins)

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


from typing import Any, Type, TypeVar


__all__ = [
    'dataloader',
    'load',
    'datadumper',
    'dump',
]


T = TypeVar('T')


def load(value: Any, type_: Type[T], **kwargs) -> T:
    """
    Quick function call to load data into a type.

    It is useful to avoid creating the Loader object,
    in case only the default parameters are used.
    """
    from . import dataloader
    loader = dataloader.Loader(**kwargs)
    return loader.load(value, type_)


def dump(value: Any, **kwargs) -> Any:
    """
    Quick function to dump a data structure into
    something that is compatible with json or
    other programs and languages.

    It is useful to avoid creating the Dumper object,
    in case only the default parameters are used.
    """
    from . import datadumper
    dumper = datadumper.Dumper(**kwargs)
    return dumper.dump(value)


def attrload(value: Any, type_: Type[T], **kwargs) -> T:
    """
    Quick function call to load data supporting the attr module
    in addition to the default ones.
    """
    from . import dataloader
    from .plugins import attrload as loadplugin
    loader = dataloader.Loader(**kwargs)
    loadplugin.add2loader(loader)
    return loader.load(value, type_)


def attrdump(value: Any, **kwargs) -> Any:
    """
    Quick function to do a dump that supports the attr
    module.
    """
    from . import datadumper
    from .plugins import attrdump as dumpplugin
    dumper = datadumper.Dumper(**kwargs)
    dumpplugin.add2dumper(dumper)
    return dumper.dump(value)
