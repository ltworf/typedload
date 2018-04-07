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
        self.basictypes = {int, bool, float, str, NONETYPE}

    def dump(self, value: Any) -> Any:
        if type(value) in self.basictypes:
            return value
        elif issubclass(type(value), list) or issubclass(type(value), tuple) or issubclass(type(value), set):
            return [self.dump(i) for i in value]
        elif issubclass(type(value), Enum):
            return self.dump(value.value)
        raise ValueError('Unable to dump %s' % value)
