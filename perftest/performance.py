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
from pathlib import Path

def main():
    tests = [
        'load list of ints',
        'load list of floats and ints',
        'load list of NamedTuple objects',
        'load list of dataclass objects',
        'load list of attrs objects',
    ]

    outdir = Path('perftest.output')
    if not outdir.exists():
        outdir.mkdir()

    tempdir = mkdtemp()
    for i in ['common'] + tests:
        copy(f'perftest/{i}.py', tempdir)

    tags = check_output(['git', 'tag', '--list'], encoding='ascii').strip().split('\n')
    # Skip minor versions
    tags = [i for i in tags if '-' not in i and ',' not in i]
    # Sort by version
    tags.sort(key=lambda i: tuple(int(j) for j in i.split('.')))

    # Add current branch if it is not master
    current = check_output(['git', 'branch', '--show-current'], encoding='ascii').strip()
    if current != 'master':
        tags.append(current)

    plotcmd = []
    maxtime = 0

    for i in tests:
        print(f'Now running: {i}')

        with open(outdir / f'{i}.dat', 'wt') as f:
            counter = 0

            print('\tRunning test with pydantic')
            pydantic_time = float(check_output(['python3', f'{tempdir}/{i}.py', '--pydantic']))
            maxtime = maxtime if maxtime > pydantic_time else pydantic_time
            f.write(f'{counter} "pydantic" {pydantic_time}\n')
            for branch in tags[len(tags) - 10:] + ['master']:
                counter += 1
                print(f'\tRunning test with {branch}')
                check_output(['git', 'checkout', branch], stderr=DEVNULL)
                typedload_time = float(check_output(['python3', f'{tempdir}/{i}.py', '--typedload']))
                f.write(f'{counter} "{branch}" {typedload_time}\n')
                maxtime = maxtime if maxtime > typedload_time else typedload_time

            counter += 1
        plotcmd.append(f'"{i}.dat" using 1:3:xtic(2) with linespoint title "{i}"')
    rmtree(tempdir)

    gnuplot_script = outdir / 'perf.p'
    with open(gnuplot_script, 'wt') as f:
        print('set style fill solid', file=f)
        print('set ylabel "seconds"', file=f)
        print('set xlabel "package"', file=f)
        print(f'set title "typedload performance test"', file=f)
        print(f'set yrange [0:{maxtime}]', file=f)
        print('plot ' + ','.join(plotcmd), file=f)
    print(f'Gnuplot script generated in {gnuplot_script}. You can execute')
    print(f'load "{gnuplot_script}"')
    print(f'inside a gnuplot shell')


if __name__ == '__main__':
    main()
