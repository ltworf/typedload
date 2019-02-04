"""
typedload
Module to check types from the typing module.

For example is_list(List) and is_list(List[int])
return True.

It is not the same as isinstance(), it wants types, not instances.

It is expected that is_list(list) returns False, since it shouldn't be used for
type hints.

The module is useful because there is no public API to do those checks, and it
protects the user from the ever changing internal representation used in
different versions of Python.
"""

# Copyright (C) 2019 Salvo "LtWorf" Tomaselli
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

from enum import Enum
from typing import Any, Tuple, Union, Set, List, Dict, Type


try:
    # Since 3.7
    from typing import ForwardRef  # type: ignore
except ImportError:
    from typing import _ForwardRef as ForwardRef  # type: ignore


def _issubclass(t1, t2) -> bool:
    """
    Wrapper around _issubclass to circumvent python 3.7 changing API
    """
    try:
        return issubclass(t1, t2)
    except TypeError:
        return False


HAS_TUPLEARGS = hasattr(Tuple[int, int], '__args__')
NONETYPE = type(None)  # type: Type[Any]


def is_tuple(type_: Type[Any]) -> bool:
    if HAS_TUPLEARGS:
        # The tuple, Tuple thing is a difference between 3.6 and 3.7
        return getattr(type_, '__origin__', None) in {tuple, Tuple}
    else:
        # Old python
        return _issubclass(type_, Tuple) and _issubclass(type_, tuple) == False


# This is a workaround for an incompatibility between 3.5.2 and previous, and 3.5.3 and later
try:
    issubclass(Union[int,str], Union)  # type: ignore
    HAS_UNIONSUBCLASS = True
except:
    HAS_UNIONSUBCLASS = False


def is_union(type_: Type[Any]) -> bool:
    if HAS_UNIONSUBCLASS:
        # Old python
        return _issubclass(type_, Union)
    else:
        return getattr(type_, '__origin__', None) == Union


def is_nonetype(type_: Type[Any]) -> bool:
    return type_ == NONETYPE


def is_list(type_: Type[Any]) -> bool:
    return getattr(type_, '__origin__', None) in {list, List}


def is_dict(type_: Type[Any]) -> bool:
    return getattr(type_, '__origin__', None) in {dict, Dict}


def is_set(type_: Type[Any]) -> bool:
    return getattr(type_, '__origin__', None) in {set, Set}


def is_enum(type_: Type[Any]) -> bool:
    return _issubclass(type_, Enum)


def is_namedtuple(type_: Type[Any]) -> bool:
    return _issubclass(type_, tuple) and set(dir(type_)).issuperset({'_field_types', '_fields'})


def is_dataclass(type_: Type[Any]) -> bool:
    return '__dataclass_fields__' in dir(type_)


def is_forwardref(type_: Type[Any]) -> bool:
    return type(type_) == ForwardRef
