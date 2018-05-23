# typedload
# This module is the inverse of dataloader. It converts typed
# data structures to things that json can treat.

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
    'Dumper',
]


NONETYPE = type(None)


class Dumper:

    def __init__(self, **kwargs):
        """
        This dumps data structures recursively using only
        basic types, lists and dictionaries.

        A value dumped in this way from a typed data structure
        can be loaded back using dataloader.

        hidedefault: When enabled, does not include fields that
            have the same value as the default in the dump.

        raiseconditionerrors: Enabled by default.
            Raises exceptions when evaluating a condition from an
            handler. When disabled, the exceptions are not raised
            and the condition is considered False.

        handlers: This is the list that the dumper uses to
            perform its task.
            The type is:
            List[
                Tuple[
                    Callable[[Any], bool],
                    Callable[['Dumper', Any], Any]
                ]
            ]
            The elements are: Tuple[Condition,Dumper]
            Condition(value) -> Bool
            Dumper(dumper, value) -> simpler_value

            In most cases, it is sufficient to append new elements
            at the end, to handle more types.

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
        self.basictypes = {int, bool, float, str, NONETYPE}

        self.hidedefault = True

        # Raise errors if the condition fails
        self.raiseconditionerrors = True

        self.handlers = [
            (lambda value: type(value) in self.basictypes, lambda l, value: value),
            (lambda value: isinstance(value, tuple) and hasattr(value, '_fields') and hasattr(value, '_asdict'), _namedtupledump),
            (lambda value: isinstance(value, (list, tuple, set)), lambda l, value: [l.dump(i) for i in value]),
            (lambda value: isinstance(value, Enum), lambda l, value: l.dump(value.value)),
            (lambda value: isinstance(value, Dict), lambda l, value: {l.dump(k): l.dump(v) for k, v in value.items()}),
        ]  # type: List[Tuple[Callable[[Any], bool],Callable[['Dumper', Any], Any]]]

        for k, v in kwargs.items():
            setattr(self, k, v)

    def dump(self, value: Any) -> Any:
        for cond, func in self.handlers:
            try:
                r = cond(value)
            except:
                if self.raiseconditionerrors:
                    raise
                r = False
            if r:
                return func(self, value)
        raise ValueError('Unable to dump %s' % value)


def _namedtupledump(l, value):
    field_defaults = getattr(value, '_field_defaults', {})
    # Named tuple, skip default values
    return {
        k: l.dump(v) for k, v in value._asdict().items()
        if not l.hidedefault or k not in field_defaults or field_defaults[k] != v
    }
