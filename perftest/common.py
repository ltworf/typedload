# typedload
# Copyright (C) 2021 Salvo "LtWorf" Tomaselli
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


from time import monotonic as time


def timeit(f) -> float:
    '''
    f is a function taking no parameters.

    It gets called multiple times to try and reduce
    measure error.
    '''
    r = []
    for i in range(5):
        begin = time()
        f()
        end = time()
        r.append(end - begin)
    return min(r)
