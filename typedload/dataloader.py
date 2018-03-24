# typedload
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


from enum import Enum
from typing import *


__all__ = [
    'Loader',
]


class Loader:

    def __init__(self):
        # Types that do not need conversion
        self.basictypes = {int, bool, float, str}

        # If true, it attempts to do casting of basic types
        # otherwise an exception is raised
        self.basiccast = True

        # Raise errors if the value has more data than the
        # type expects.
        # By default the extra data is ignored.
        self.failonextra = False

    def _basicload(self, value: Any, type_: type) -> Any:
        """
        This converts a value into a basic type.

        In theory it does nothing, but it performs type checking
        and raises if conditions fail.

        It also attempts casting, if enabled.
        """

        if type_ not in self.basictypes:
            raise TypeError('Type %s is not a basic type' % type_)

        if type(value) != type_:
            if self.basiccast:
                return type_(value)
            else:
                raise TypeError('%s is not of type %s' % (value, type_))
        return value

    def _listload(self, value, type_: type) -> List:
        """
        This loads into something like List[int]
        """
        t = type_.__args__[0]
        return [self.load(v, t) for v in value]

    def _dictload(self, value, type_: type) -> Dict:
        """
        This loads into something like Dict[str,str]

        Recursively loads both keys and values.
        """
        key_type, value_type = type_.__args__
        return {self.load(k, key_type): self.load(v, value_type) for k, v in value.items()}

    def _setload(self, value, type_: type) -> Set:
        """
        This loads into something like Set[int]
        """
        t = type_.__args__[0]
        return {self.load(i, t) for i in value}

    def _tupleload(self, value, type_: type) -> Tuple:
        """
        This loads into something like Tuple[int,str]
        """
        if self.failonextra and len(value) > len(type_.__args__):
            raise ValueError('Value %s is too long for type %s' % (value, type_))
        elif len(value) < len(type_.__args__):
            raise ValueError('Value %s is too short for type %s' % (value, type_))

        return tuple(self.load(v, t) for v, t in zip(value, type_.__args__))

    def load(self, value: Any, type_: type) -> Any:

        if type_ in self.basictypes:
            return self._basicload(value, type_)
        elif issubclass(type_, Enum):
            return type_(value)
        elif issubclass(type_, tuple) and getattr(type_, '__origin__', None) == Tuple:
            return self._tupleload(value, type_)
        elif issubclass(type_, list) and getattr(type_, '__origin__', None) == List:
            return self._listload(value, type_)
        elif issubclass(type_, dict) and getattr(type_, '__origin__', None) == Dict:
            return self._dictload(value, type_)
        elif issubclass(type_, set) and getattr(type_, '__origin__', None) == Set:
            return self._setload(value, type_)
        else:
            raise TypeError('Cannot deal with value %s of type %s' % (value, type_))
