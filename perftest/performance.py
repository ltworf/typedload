#!/usr/bin/env python3
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


from subprocess import check_output, DEVNULL
from tempfile import mkdtemp
from shutil import copy, rmtree


def main():
    tests = [
        'perf_intlist',
    ]

    tempdir = mkdtemp()
    for i in tests:
        copy(f'perftest/{i}.py', tempdir)


    tags = check_output(['git', 'tag', '--list'], encoding='ascii').strip().split('\n')

    for i in tests:
        print(f'Now running: {i}')

        with open(f'{i}.dat', 'wt') as f:
            counter = 0

            print('\tRunning test with pydantic')
            pydantic_time = float(check_output(['python3', f'{tempdir}/{i}.py', '--pydantic']))
            f.write(f'{counter} "pydantic" {pydantic_time}\n')
            for branch in tags[len(tags)-4:] + ['master']:
                counter += 1
                print(f'\tRunning test with {branch}')
                check_output(['git', 'checkout', branch], stderr=DEVNULL)
                typedload_time = float(check_output(['python3', f'{tempdir}/{i}.py', '--typedload']))
                f.write(f'{counter} "typedload {branch}" {typedload_time}\n')

            counter += 1
            f.write(f'{counter} "0" {0}\n')
    rmtree(tempdir)


if __name__ == '__main__':
    main()
