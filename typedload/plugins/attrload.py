"""
typedload
Module to load data into data structures from the "attr" module

Name mangling is supported by having a 'name' attribute in the metadata

@attr.s
class Example:
    attribute = attr.ib(type=int, metadata={'name': 'att.rib.ute:name'}

The dictionary key for 'attribute' will be 'att.rib.ute:name'.

This is very useful for keys that use invalid or reserved characters that
can't be used in variable names.
Another common application is to convert camelCase into not_camel_case.
"""

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


from ..dataloader import _namedtupleload
from ..exceptions import *
from ..typechecks import is_attrs

class _FakeNamedTuple(tuple):
    """
    This class simulates a Python3.6 NamedTuple
    instance.

    It has the same hidden fields, so the same
    loader for the NamedTuple.

    It needs to be created with fields, field_types, field_defaults
    """

    def __new__(cls, fields):
        return super(_FakeNamedTuple, cls).__new__(cls, tuple(fields))

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
        try:
            return self[3](**kwargs)
        except TypeError as e:
            raise TypedloadTypeError(str(e), type_=self[3], value=kwargs)
        except Exception as e:
            raise TypedloadException(str(e), type_=self[3], value=kwargs)


def _attrload(l, value, type_):
    if not isinstance(value, dict):
        raise TypedloadTypeError('Expected dictionary, got %s' % type(value), type_=type_, value=value)
    value = value.copy()
    names = []
    defaults = {}
    types = {}

    for attribute in type_.__attrs_attrs__:
        names.append(attribute.name)
        types[attribute.name] = attribute.type
        defaults[attribute.name] = attribute.default

        # Manage name mangling
        if 'name' in attribute.metadata:
            dataname = attribute.metadata['name']
            pyname = attribute.name

            if dataname in value:
                tmp = value[dataname]
                del value[dataname]
                value[pyname] = tmp

    t = _FakeNamedTuple((
        tuple(names),
        types,
        defaults,
        type_,
    ))

    return _namedtupleload(l, value, t)


def add2loader(l) -> None:
    """
    Adds the "attr" handler to an existing loader
    """
    l.handlers.append((is_attrs, _attrload))
