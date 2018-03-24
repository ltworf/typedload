# loadtyped
# Copyright (C) 2018 Salvo "LtWorf" Tomaselli
#
# loadtyped is free software: you can redistribute it and/or modify
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


from typing import *


class Loader:

    def __init__(self):
        # Types that do not need conversion
        self.basictypes = {int, bool, float, str}

        # If true, it attempts to do casting of basic types
        # otherwise an exception is raised
        self.basiccast = True

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

    def load(self, value: Any, type_: type):

        if type_ in self.basictypes:
            return self._basicload(value, type_)
        else:
            raise TypeError('Cannot deal with value %s of type %s' % (value, type_))
