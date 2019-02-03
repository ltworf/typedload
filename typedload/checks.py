"""
typedload
Module to check types
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
from typing import *

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

if HAS_TUPLEARGS:
    tuple_check = lambda type_: getattr(type_, '__origin__', None) in {tuple, Tuple}
else:
    # Old python
    tuple_check = lambda type_: _issubclass(type_, Tuple) and _issubclass(type_, tuple) == False


# This is a workaround for an incompatibility between 3.5.2 and previous, and 3.5.3 and later
try:
    issubclass(Union[int,str], Union)  # type: ignore
    HAS_UNIONSUBCLASS = True
except:
    HAS_UNIONSUBCLASS = False

if HAS_UNIONSUBCLASS:
    # Old python
    union_check = lambda type_: _issubclass(type_, Union)
else:
    union_check = lambda type_: getattr(type_, '__origin__', None) == Union

list_check = lambda type_: getattr(type_, '__origin__', None) in {list, List}
dict_check = lambda type_: getattr(type_, '__origin__', None) in {dict, Dict}
set_check = lambda type_: getattr(type_, '__origin__', None) in {set, Set}
enum_check = lambda type_: _issubclass(type_, Enum)
namedtuple_check = lambda type_: _issubclass(type_, tuple) and set(dir(type_)).issuperset({'_field_types', '_fields'})
dataclass_check = lambda type_: '__dataclass_fields__' in dir(type_)
forwardref_check = lambda type_: type(type_) == ForwardRef
