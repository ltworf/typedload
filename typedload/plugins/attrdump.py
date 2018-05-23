# typedload
# Module to load data into data structures from the "attr" module
#
# Name mangling is supported by having a 'name' attribute in the metadata
#
# @attr.s
# class Example:
#     attribute = attr.ib(type=int, metadata={'name': 'att.rib.ute:name'}
#
# The dictionary key for 'attribute' will be 'att.rib.ute:name'.
#
# This is very useful for keys that use invalid or reserved characters that
# can't be used in variable names.
# Another common application is to convert camelCase into not_camel_case.

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


from typing import Any, Dict


def _condition(value: Any) -> bool:
    return hasattr(value, '__attrs_attrs__')


def _attrdump(d, value) -> Dict[str, Any]:
    r = {}
    for attr in value.__attrs_attrs__:
        attrval = getattr(value, attr.name)
        if not attr.repr:
            continue
        if not (d.hidedefault and attrval == attr.default):
            name = attr.metadata.get('name', attr.name)
            r[name] = d.dump(attrval)
    return r


def add2dumper(l) -> None:
    l.handlers.append((_condition, _attrdump))
