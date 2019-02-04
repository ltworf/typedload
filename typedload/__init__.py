"""
typedload
=========

This library loads Python data structures into
more strict data structures.

The main purpose is to load things that come from
json, bson or similar into NamedTuple.

For example this Json:
   {
       'users': [
           {
               'username': 'salvo',
               'shell': 'bash',
               'sessions': ['pts/4', 'tty7', 'pts/6']
           },
           {
               'username': 'lop'
           }
       ],
   }

Can be treated more easily if loaded into this:

class User(NamedTuple):
   username: str
   shell: str = 'bash'
   sessions: List[str] = []

class Logins(NamedTuple):
   users: List[User]

And can then be loaded with

typedload.load(data, Logins)

Simple API
==========

typedload.load() and typedload.dump() are functions to quickly load and dump
data using the default objects.

They create a new loader/dumper object with default parameters, and
discard it after.

The functions typedload.attrload() and typedload.attrdump() are similar, but
import the optional "attr" module and use an handler to deal with the
classes provided by that module.

Classes
=======

The loader and dumper classes expose a number of attributes that can be
customised to tweak their behaviour.

Handlers
========

An important way to tweak the behaviour of a loader or dumper object is
to modify the handlers list.

The handlers' list items are tuples for two functions. The signatures are
different for loader or dumper.

The first function returns a boolean, and if the value is true, the object
will call the second function and return its result.

Basically a loader and a dumper class have no functionality (but come with
a default list of handlers).

So, to add support for a new type, it is sufficient to write a function that
outputs the desired value, and a function that decides when to call that.

The index() function returns the position of handlers in the list, so that
it is possible to remove them or add new handlers before or after a given
handler.

The pointer to the loader or dumper object is passed, so that the attributes
in use for that particular object are available.

For example, if we want to add a special loader that when loading the int 42
into a string returns 'quarantadue', we can do this:

from typedload.dataloader import Loader
l = Loader()
l.handlers.insert(
    l.index(str), # This will place this entry before the string handler
    (
        lambda x: x == str,
        lambda loader, value, type_: str(value) if value != 42 else 'quarantadue'
    )
)

Then this will happen:

In [15]: l.load(12, str)
Out[15]: '12'

In [16]: l.load(42, str)
Out[16]: 'quarantadue'

This can of course be used also for use cases that make sense.

The handlers must generate exceptions from the typedload.exceptions
module.
"""

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
    'attrload',
    'attrdump',
    'typechecks',
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
    Quick function call to load data supporting the "attr" module
    in addition to the default ones.
    """
    from . import dataloader
    from .plugins import attrload as loadplugin
    loader = dataloader.Loader(**kwargs)
    loadplugin.add2loader(loader)
    return loader.load(value, type_)


def attrdump(value: Any, **kwargs) -> Any:
    """
    Quick function to do a dump that supports the "attr"
    module.
    """
    from . import datadumper
    from .plugins import attrdump as dumpplugin
    dumper = datadumper.Dumper(**kwargs)
    dumpplugin.add2dumper(dumper)
    return dumper.dump(value)
