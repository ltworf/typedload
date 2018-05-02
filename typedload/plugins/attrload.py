# typedload
# Module to load data into data structures from the "attr" module

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


from ..dataloader import _namedtupleload

class _FakeNamedTuple(tuple):
    """
    This class simulates a Python3.6 NamedTuple
    instance.

    It has the same hidden fields, so the same
    loader for the NamedTuple.

    It needs to be created with fields, field_types, field_defaults
    """

    def __new__(cls, fields):
        return super(_FakeNamedTuple, cls).__new__(cls, tuple(fields))  # type: ignore

    @property
    def _fields(self):
        return self[0]

    @property
    def _field_types(self):
        return self[1]

    @property
    def _field_defaults(self):
        return self[2]

    def __call__(self, **kwargs):
        return self[3](**kwargs)


def _attrload(l, value, type_):
    names = []
    defaults = {}
    types = {}

    for attribute in type_.__attrs_attrs__:
        names.append(attribute.name)
        types[attribute.name] = attribute.type
        defaults[attribute.name] = attribute.default

    t = _FakeNamedTuple((
        tuple(names),
        types,
        defaults,
        type_,
    ))

    return _namedtupleload(l, value, t)


def _condition(t) -> bool:
    return hasattr(t, '__attrs_attrs__')


def add2loader(l) -> None:
    l.handlers.append((_condition, _attrload))
