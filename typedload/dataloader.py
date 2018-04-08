# typedload
# Module to load data into typed data structures

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


NONETYPE = type(None)
T = TypeVar('T')


class Loader:
    """
    A loader object that recursively loads data into
    the desired type.

    basictypes: a set of types that are considered as
        building blocks for everything else and do not
        need to be converted further.
        If you are not loading from json, you probably
        want to add bytes to the set.

    failonextra: When enabled, the loader will raise
        exceptions if there are fields in the data that
        are not being used by the type.

    basiccast: When enabled, instead of trying to perform
        casts, exceptions will be raised.
        Since many json seem to encode numbers as strings,
        to avoid extra complications this functionality is
        provided.
        If you know that your original data is encoded
        properly, it is better to disable this.


    There is support for:
        * Basic python types (int, str, bool, float, NoneType)
        * NamedTuple
        * Enum
        * Optional[SomeType]
        * List[SomeType]
        * Dict[TypeA, TypeB]
        * Tuple[TypeA, TypeB, TypeC]
        * Set[SomeType]
        * Union[TypeA, TypeB]

    Using unions is complicated. If the types in the union are too
    similar to each other, it is easy to obtain an unexpected type.
    """

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

        if type(value) != type_:
            if self.basiccast:
                return type_(value)
            else:
                raise ValueError('%s is not of type %s' % (value, type_))
        return value

    def _listload(self, value, type_) -> List:
        """
        This loads into something like List[int]
        """
        t = type_.__args__[0]
        return [self.load(v, t) for v in value]

    def _dictload(self, value, type_) -> Dict:
        """
        This loads into something like Dict[str,str]

        Recursively loads both keys and values.
        """
        key_type, value_type = type_.__args__
        return {self.load(k, key_type): self.load(v, value_type) for k, v in value.items()}

    def _setload(self, value, type_) -> Set:
        """
        This loads into something like Set[int]
        """
        t = type_.__args__[0]
        return {self.load(i, t) for i in value}

    def _tupleload(self, value, type_) -> Tuple:
        """
        This loads into something like Tuple[int,str]
        """
        if self.failonextra and len(value) > len(type_.__args__):
            raise ValueError('Value %s is too long for type %s' % (value, type_))
        elif len(value) < len(type_.__args__):
            raise ValueError('Value %s is too short for type %s' % (value, type_))

        return tuple(self.load(v, t) for v, t in zip(value, type_.__args__))

    def _namedtupleload(self, value: Dict[str, Any], type_) -> Tuple:
        """
        This loads a Dict[str, Any] into a NamedTuple.
        """
        fields = set(type_._fields)
        optaional_fields = set(type_._field_defaults.keys())
        necessary_fields = fields.difference(optaional_fields)
        vfields = set(value.keys())

        if necessary_fields.intersection(vfields) != necessary_fields:
            raise ValueError(
                'Value %s does not contain fields: %s which are necessary for type %s' % (
                    value,
                    necessary_fields.difference(vfields),
                    type_
                )
            )

        if self.failonextra and len(vfields.difference(fields)):
            raise ValueError('Dictionary %s has unrecognized fields and cannot be loaded into %s' % (value, type_))

        type_hints = get_type_hints(type_)

        params = {}
        for k, v in value.items():
            if k not in fields:
                continue
            params[k] = self.load(v, type_hints[k])
        return type_(**params)

    def _unionload(self, value, type_) -> Any:
        """
        Loads a value into a union.

        Basically this iterates all the types inside the
        union, until one that doesn't raise an exception
        is found.

        If no suitable type is found, an exception is raised.
        """

        # Do not convert basic types, if possible
        if type(value) in set(type_.__args__).intersection(self.basictypes):
            return value

        exceptions = []

        # Try all types
        for t in type_.__args__:
            try:
                return self.load(value, t)
            except Exception as e:
                exceptions.append(str(e))
        raise ValueError(
            'Value %s could not be loaded into %s\n\nConversion exceptions were:\n%s' % (
                value,
                type_,
                '\n'.join(exceptions)
            )
        )

    def _enumload(self, value, type_) -> Enum:
        """
        This loads something into an Enum.

        It tries with basic types first.

        If that fails, it tries to look for type annotations inside the
        Enum, and tries to use those to load the value into something
        that is compatible with the Enum.

        Of course if that fails too, a ValueError is raised.
        """
        try:
            # Try naïve conversion
            return type_(value)  # type: ignore
        except:
            pass

        # Try with the typing hints
        for _, t in get_type_hints(type_).items():
            try:
                return type_(self.load(value, t))
            except:
                pass
        raise ValueError('Value %s could not be loaded into %s' % (value, type_))

    def load(self, value: Any, type_: Type[T]) -> T:
        """
        Loads value into the typed data structure.

        TypeError is raised if there is no known way to treat type_,
        otherwise all errors raise a ValueError.
        """
        if type_ == NONETYPE:
            if value is None:
                return None
            raise ValueError('%s is not None' % value)
        elif getattr(type_, '__origin__', None) == Union:
            return self._unionload(value, type_)
        elif type_ in self.basictypes:
            return self._basicload(value, type_)
        elif issubclass(type_, Enum):
            return self._enumload(value, type_)  # type: ignore
        elif issubclass(type_, tuple) and getattr(type_, '__origin__', None) == Tuple:
            return self._tupleload(value, type_)
        elif issubclass(type_, list) and getattr(type_, '__origin__', None) == List:
            return self._listload(value, type_)  # type: ignore
        elif issubclass(type_, dict) and getattr(type_, '__origin__', None) == Dict:
            return self._dictload(value, type_)  # type: ignore
        elif issubclass(type_, set) and getattr(type_, '__origin__', None) == Set:
            return self._setload(value, type_)  # type: ignore
        elif issubclass(type_, tuple) and set(dir(type_)).issuperset({'_field_defaults', '_field_types', '_fields'}):
            return self._namedtupleload(value, type_)
        else:
            raise TypeError('Cannot deal with value %s of type %s' % (value, type_))
