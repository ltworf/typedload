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

    def __init__(self):
        """
        This dumps data structures recursively using only
        basic types, lists and dictionaries.

        A value dumped in this way from a typed data structure
        can be loaded back using dataloader.

        hidedefault: When enabled, does not include fields that
            have the same value as the default in the dump.

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

    def dump(self, value: Any) -> Any:
        if type(value) in self.basictypes:
            return value
        elif isinstance(value, tuple) and {'_fields', '_field_defaults', '_asdict'}.issubset(set(dir(value))):
            # Named tuple, skip default values
            return {
                k: self.dump(v) for k, v in value._asdict().items()  # type: ignore
                if not self.hidedefault or k not in value._field_defaults or value._field_defaults[k] != v  # type: ignore
            }
        elif isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
            return [self.dump(i) for i in value]
        elif isinstance(value, Enum):
            return self.dump(value.value)
        elif isinstance(value, Dict):
            return {self.dump(k): self.dump(v) for k, v in value.items()}
        raise ValueError('Unable to dump %s' % value)
