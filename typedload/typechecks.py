"""
typedload
Module to check types, mostly from the typing module.

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
from typing import Any, Tuple, Union, Set, List, Dict, Type, FrozenSet


__all__ = [
    'is_attrs',
    'is_dataclass',
    'is_dict',
    'is_enum',
    'is_forwardref',
    'is_frozenset',
    'is_list',
    'is_namedtuple',
    'is_nonetype',
    'is_set',
    'is_tuple',
    'is_union',
    'uniontypes',
    'NONETYPE',
    'HAS_TUPLEARGS',
    'HAS_UNIONSUBCLASS',
]


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
    '''
    Tuple[int, str]
    Tuple
    '''
    if HAS_TUPLEARGS:
        # The tuple, Tuple thing is a difference between 3.6 and 3.7
        # In 3.6 and before, Tuple had an __extra__ field, while Tuple[something]
        # would have the normal __origin__ field.
        #
        # Those apply for Dict, List, Set, Tuple
        return _generic_type_check(type_, tuple, Tuple)
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
    '''
    Union[A, B]
    Union
    Optional[A]
    '''
    if HAS_UNIONSUBCLASS:
        # Old python
        return _issubclass(type_, Union)
    else:
        return getattr(type_, '__origin__', None) == Union


def is_nonetype(type_: Type[Any]) -> bool:
    '''
    type_ == type(None)
    '''
    return type_ == NONETYPE


def _generic_type_check(type_: Type[Any], native, from_typing):
    return getattr(type_, '__origin__', None) in {native, from_typing} or getattr(type_, '__extra__', None) == native


def is_list(type_: Type[Any]) -> bool:
    '''
    List[A]
    List
    '''
    return _generic_type_check(type_, list, List)


def is_dict(type_: Type[Any]) -> bool:
    '''
    Dict[A, B]
    Dict
    '''
    return _generic_type_check(type_, dict, Dict)


def is_set(type_: Type[Any]) -> bool:
    '''
    Set[A]
    Set
    '''
    return _generic_type_check(type_, set, Set)


def is_frozenset(type_: Type[Any]) -> bool:
    '''
    FrozenSet[A]
    FrozenSet
    '''
    return _generic_type_check(type_, frozenset, FrozenSet)


def is_enum(type_: Type[Any]) -> bool:
    '''
    Check if the class is a subclass of Enum
    '''
    return _issubclass(type_, Enum)


def is_namedtuple(type_: Type[Any]) -> bool:
    '''
    Generated with typing.NamedTuple
    '''
    return _issubclass(type_, tuple) and hasattr(type_, '_field_types') and hasattr(type_, '_fields')


def is_dataclass(type_: Type[Any]) -> bool:
    '''
    dataclass (Introduced in Python3.7
    '''
    return hasattr(type_, '__dataclass_fields__')


def is_forwardref(type_: Type[Any]) -> bool:
    '''
    Check if it's a ForwardRef.

    They are unresolved types passed as strings, supposed to
    be resolved into types at a later moment
    '''
    return type(type_) == ForwardRef


def is_attrs(type_: Type[Any]) -> bool:
    '''
    Check if the type is obtained with an
    @attr.s decorator
    '''
    return hasattr(type_, '__attrs_attrs__')


def uniontypes(type_: Type[Any]) -> Set[Type[Any]]:
    '''
    Returns the types of a Union.

    Raises ValueError if the argument is not a Union
    and AttributeError when running on an unsupported
    Python version.
    '''
    if not is_union(type_):
        raise ValueError('Not a Union: ' + str(type_))

    if hasattr(type_, '__args__'):
        return set(type_.__args__)
    elif hasattr(type_, '__union_params__'):
        return set(type_.__union_params__)
    raise AttributeError('The typing API for this Python version is unknown')
