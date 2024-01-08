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

# Copyright (C) 2019-2023 Salvo "LtWorf" Tomaselli
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
import sys
from enum import Enum
from re import Pattern
from typing import Any, Tuple, Union, Set, List, Dict, Type, FrozenSet, NewType


__all__ = [
    'is_any',
    'is_pattern',
    'is_attrs',
    'is_dataclass',
    'is_dict',
    'is_enum',
    'is_forwardref',
    'is_frozenset',
    'is_list',
    'is_literal',
    'is_namedtuple',
    'is_nonetype',
    'is_set',
    'is_tuple',
    'is_union',
    'is_typeddict',
    'is_newtype',
    'is_optional',
    'is_notrequired',
    'notrequiredtype',
    'uniontypes',
    'literalvalues',
    'NONETYPE',
    'HAS_TUPLEARGS',
    'HAS_UNIONSUBCLASS',
]


from typing import ForwardRef, Literal
from typing import _TypedDictMeta  # type: ignore

UnionType = None  # type: Any
try:
    # Since 3.10
    from types import UnionType  # type: ignore
except ImportError:
    pass


try:
    # Since 3.11
    from typing import NotRequired  # type: ignore
except ImportError:
    NotRequired = None


def _issubclass(t1, t2) -> bool:
    """
    Wrapper around _issubclass to circumvent python 3.7 changing API
    """
    try:
        return issubclass(t1, t2)
    except TypeError:
        return False


HAS_TUPLEARGS = True # Legacy, used to be dependant on python version, but I exported the symbol
NONETYPE = type(None)  # type: Any
HAS_UNIONSUBCLASS = False


def is_tuple(type_: Any) -> bool:
    '''
    Tuple[int, str]
    Tuple
    '''
    return _generic_type_check(type_, tuple, Tuple)


if UnionType:
    # Uniontype is 3.10 defined on 3.10 and None otherwise
    def is_union(type_: Any) -> bool:
        '''
        Union[A, B]
        Union
        Optional[A]
        A | B
        '''
        return getattr(type_, '__origin__', None) == Union or getattr(type_, '__class__', None) == UnionType
else:
    def is_union(type_: Any) -> bool:
        '''
        Union[A, B]
        Union
        Optional[A]
        '''

        # Uniontype is 3.10 defined on 3.10 and None otherwise
        return getattr(type_, '__origin__', None) == Union


def is_optional(type_: Any) -> bool:
    '''
    Optional[int]
    int | None

    Note that Optional is just a Union, so if is_optional is True then
    also is_union will be True
    '''
    return is_union(type_) and (len(type_.__args__) == 2) and NONETYPE in type_.__args__


def is_nonetype(type_: Any) -> bool:
    '''
    type_ == type(None)
    '''
    return type_ == NONETYPE


def _generic_type_check(type_: Any, native, from_typing) -> bool:
    return getattr(type_, '__origin__', None) in {native, from_typing} or getattr(type_, '__extra__', None) == native


def is_list(type_: Any) -> bool:
    '''
    List[A]
    List
    '''
    return _generic_type_check(type_, list, List)


def is_dict(type_: Any) -> bool:
    '''
    Dict[A, B]
    Dict
    '''
    return _generic_type_check(type_, dict, Dict)


def is_set(type_: Any) -> bool:
    '''
    Set[A]
    Set
    '''
    return _generic_type_check(type_, set, Set)


def is_frozenset(type_: Any) -> bool:
    '''
    FrozenSet[A]
    FrozenSet
    '''
    return _generic_type_check(type_, frozenset, FrozenSet)


def is_enum(type_: Any) -> bool:
    '''
    Check if the class is a subclass of Enum
    '''
    return _issubclass(type_, Enum)


def is_namedtuple(type_: Any) -> bool:
    '''
    Generated with typing.NamedTuple
    '''
    return _issubclass(type_, tuple) and hasattr(type_, '__annotations__') and hasattr(type_, '_fields')


def is_dataclass(type_: Any) -> bool:
    '''
    dataclass (Introduced in Python3.7
    '''
    return hasattr(type_, '__dataclass_fields__')


def is_forwardref(type_: Any) -> bool:
    '''
    Check if it's a ForwardRef.

    They are unresolved types passed as strings, supposed to
    be resolved into types at a later moment
    '''
    return type(type_) == ForwardRef


def is_attrs(type_: Any) -> bool:
    '''
    Check if the type is obtained with an
    @attr.s decorator
    '''
    return hasattr(type_, '__attrs_attrs__')


if sys.version_info > (3, 10, 0):
    def is_newtype(type_: Any) -> bool:
        return type(type_) == NewType

else:
    def is_newtype(type_: Any) -> bool:
        return hasattr(type_, '__supertype__')


def uniontypes(type_: Any) -> Tuple[Type[Any], ...]:
    '''
    Returns the types of a Union.
    '''
    return type_.__args__


def literalvalues(type_: Any) -> Set[Any]:
    '''
    Returns the values of a Literal

    Raises ValueError if the argument is not a Literal
    '''
    if not is_literal(type_):
        raise ValueError('Not a Literal: ' + str(type_))
    return set(type_.__args__)


def is_literal(type_: Any) -> bool:
    '''
    Check if the type is a typing.Literal
    '''
    return getattr(type_, '__origin__', None) == Literal


def is_pattern(type_: Any) -> bool:
    '''
    Check if the type is a re.Pattern
    '''
    return type_ == Pattern or getattr(type_, "__origin__", None) == Pattern


def is_typeddict(type_: Any) -> bool:
    '''
    Check if it is a typing.TypedDict
    '''
    return isinstance(type_, _TypedDictMeta)


def is_any(type_: Any) -> bool:
    '''
    Check if it is a typing.Any
    '''
    return type_ == Any


if NotRequired:
    def is_notrequired(type_: Any) -> bool:
        '''
        Check if it's typing.NotRequired or typing_extensions.NotRequired
        '''
        return getattr(type_, '__origin__', None) == NotRequired
else:
    def is_notrequired(type_: Any) -> bool:
        '''
        Returns False.
        NotRequired is not defined on this platform.
        '''
        return False


def notrequiredtype(type_: Any) -> Type[Any]:
    '''
    Return the type wrapped by NotRequired
    '''
    return type_.__args__[0]


def discriminatorliterals(type_: Any) -> Dict[str, Set[Any]]:
    """
    Takes an object type (NamedTuple, TypedDict, attrs, dataclass)
    and returns which fields take a literal and which values are
    allowed by the literal.

    For unknown types, an empty dictionary is returned.

    Since Literal exists only since 3.8, for previous versions
    this always returns an empty dictionary
    """

    # Give up if the object is unknown
    try:
        d = type_.__annotations__.items()
    except AttributeError:
        return {}

    r = {}
    for k, v in d:
        if not is_literal(v):
            continue
        r[k] = literalvalues(v)
    return r
