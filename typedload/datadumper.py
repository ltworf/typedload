"""
typedload
This module is the inverse of dataloader. It converts typed
data structures to things that json can serialize.
"""
# Copyright (C) 2018-2021 Salvo "LtWorf" Tomaselli
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

import datetime
import ipaddress
from inspect import signature
from enum import Enum
import pathlib
from typing import *

from .exceptions import TypedloadValueError
from .typechecks import is_attrs, NONETYPE


__all__ = [
    'Dumper',
]


class Dumper:
    """
    This dumps data structures recursively using only
    basic types, lists and dictionaries.

    A value dumped in this way from a typed data structure
    can be loaded back using dataloader.

    hidedefault: Enabled by default.
        When enabled, does not include fields that have the
        same value as the default in the dump.

    raiseconditionerrors: Enabled by default.
        Raises exceptions when evaluating a condition from an
        handler. When disabled, the exceptions are not raised
        and the condition is considered False.

    mangle_key: Defaults to 'name'
        Specifies which key is used into the metadata dictionaries
        to perform name-mangling.

    handlers: This is the list that the dumper uses to
        perform its task.
        The type is:
        List[
            Tuple[
                Callable[[Any], bool],
                Callable[['Dumper', Any], Any]
            ]
        ]
        The elements are: Tuple[Condition, Dumper]
        Condition(value) -> Bool
        Dumper(dumper, value) -> simpler_value

        In most cases, it is sufficient to append new elements
        at the end, to handle more types.

    strconstructed: Set of types to dump to a string.

    These parameters can be set as named arguments in the constructor
    or they can be set later on.

    The constructor will accept any named argument, but only the documented
    ones have any effect. This is to allow custom handlers to have their
    own parameters as well.

    There is support for:
        * Basic python types (int, str, bool, float, NoneType)
        * NamedTuple
        * Enum
        * List[SomeType]
        * Dict[TypeA, TypeB]
        * Tuple[TypeA, TypeB, TypeC]
        * Set[SomeType]
    """
    def __init__(self, **kwargs) -> None:
        self.basictypes = {int, bool, float, str, NONETYPE}

        self.hidedefault = True

        # Which key is used in metadata to perform name mangling
        self.mangle_key = 'name'

        # Raise errors if the condition fails
        self.raiseconditionerrors = True

        # Things that become str. Needs to be done before handlers are created
        if 'strconstructed' in kwargs:
            self.strconstructed = kwargs.pop('strconstructed')
        else:
            self.strconstructed = {
                pathlib.Path,
                pathlib.PosixPath,
                pathlib.WindowsPath,
                ipaddress.IPv4Address,
                ipaddress.IPv6Address,
                ipaddress.IPv4Network,
                ipaddress.IPv6Network,
                ipaddress.IPv4Interface,
                ipaddress.IPv6Interface,
            }

        self.handlers = [
            (lambda value: type(value) in self.basictypes, lambda l, value, t: value),
            (lambda value: isinstance(value, tuple) and hasattr(value, '_fields') and hasattr(value, '_asdict'), _namedtupledump),
            (lambda value: '__dataclass_fields__' in dir(value), _dataclassdump),
            (lambda value: isinstance(value, (list, tuple, set, frozenset)), _iteratordump),
            (lambda value: isinstance(value, Enum), lambda l, value, t: l.dump(value.value)),
            (lambda value: isinstance(value, Dict), lambda l, value, t: {l.dump(k): l.dump(v) for k, v in value.items()}),
            (is_attrs, _attrdump),
            (lambda value: isinstance(value, (datetime.date, datetime.time)), _datetimedump),
            (lambda value: type(value) in self.strconstructed, lambda l, value, t: str(value)),

        ]  # type: List[Tuple[Callable[[Any], bool], Callable[['Dumper', Any, Any], Any]|Callable[['Dumper', Any], Any]]]

        self._handlerscache = {}  # type: Dict[Type[Any], Callable[['Dumper', Any], Any]|Callable[['Dumper', Any, Any], Any]]
        self._dataclasscache = {}  # type: Dict[Type[Any], Tuple[Set[str], Dict[str, Any], Dict[str, Any]]]

        for k, v in kwargs.items():
            setattr(self, k, v)

    def index(self, value: Any) -> int:
        """
        Returns the index in the handlers list
        that matches the given value.

        If no condition matches, ValueError is raised.
        """
        for i, cond in ((j[0], j[1][0]) for j in enumerate(self.handlers)):
            try:
                match = cond(value)
            except:
                if self.raiseconditionerrors:
                    raise
                match = False
            if match:
                return i
        raise TypedloadValueError('Unable to dump %s' % value, value=value, type_=type(value))

    def dump(self, value: Any, annotated_type=Any) -> Any:
        """
        Dump the typed data structure into its
        untyped equivalent.

        annotated_type contains the annotation for the value.
        It is not needed to provide it, but it can enable some faster code paths.
        """
        t = type(value)
        func = self._handlerscache.get(t)
        if func is None:
            index = self.index(value)
            f = self.handlers[index][1]
            # It has no type parameter
            # TODO make all handlers require it in 3.0
            if len(signature(f).parameters) == 2:
                func = lambda d, v, _: f(d, v)  # type: ignore
            else:
                func = f
            self._handlerscache[t] = func
        return func(self, value, annotated_type)  # type: ignore


def _attrdump(d, value, t) -> Dict[str, Any]:
    r = {}
    for attr in value.__attrs_attrs__:
        attrval = getattr(value, attr.name)
        if not attr.repr:
            continue
        if d.hidedefault:
            if attrval == attr.default:
                continue
            elif hasattr(attr.default, 'factory') and attrval == attr.default.factory():
                continue
        name = attr.metadata.get(d.mangle_key, attr.name)
        r[name] = d.dump(attrval)
    return r


def _datetimedump(d: Dumper, value: Union[datetime.time, datetime.date, datetime.datetime], t):
    # datetime is subclass of date
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return [value.year, value.month, value.day]
    if value.tzinfo is not None:
        raise NotImplementedError('Dumping of tzdata object is not supported')
    if isinstance(value, datetime.time):
        return [value.hour, value.minute, value.second, value.microsecond]
    # datetime.datetime
    return [value.year, value.month, value.day, value.hour, value.minute, value.second, value.microsecond]


def _namedtupledump(d: Dumper, value, t) -> Dict[str, Any]:
    field_defaults = getattr(value, '_field_defaults', {})
    # Named tuple, skip default values
    return {
        k: d.dump(v) for k, v in value._asdict().items()
        if not d.hidedefault or k not in field_defaults or field_defaults[k] != v
    }


def _dataclassdump(d: Dumper, value, t) -> Dict[str, Any]:
    t = type(value)
    cached = d._dataclasscache.get(t)
    if cached is None:
        from dataclasses import _MISSING_TYPE as DT_MISSING_TYPE
        fields = set(value.__dataclass_fields__.keys())
        field_defaults = {k: v.default for k,v in value.__dataclass_fields__.items() if not isinstance (v.default, DT_MISSING_TYPE)}
        field_factories = {k: v.default_factory() for k,v in value.__dataclass_fields__.items() if not isinstance (v.default_factory, DT_MISSING_TYPE)}
        defaults = {**field_defaults, **field_factories} # Merge the two dictionaries
        type_hints = get_type_hints(value)
        d._dataclasscache[t] = (fields, defaults, type_hints)
    else:
        fields, defaults, type_hints = cached

    r = {
        value.__dataclass_fields__[f].metadata.get(d.mangle_key, f) : d.dump(getattr(value, f), type_hints.get(f, Any)) for f in fields
        if not d.hidedefault or f not in defaults or defaults[f] != getattr(value, f)
    }
    return r

def _iteratordump(d: Dumper, value: Any, t: Any) -> List[Any]:
    itertype = getattr(t, '__args__', (Any, ))
    if len(itertype) == 1 and (itertype[0] in d.basictypes):
        r = []
        iterator = iter(value)
        try:
            # Call one iteration with dump, to populate the cache
            r.append(d.dump(next(iterator), itertype[0]))
        except StopIteration:
            return []
        f = d._handlerscache[itertype[0]]  # type: ignore
        r.extend((f(d, i, itertype[0]) for i in iterator))  # type: ignore
        return r
    else:
        return [d.dump(i) for i in value]
