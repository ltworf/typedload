#!/usr/bin/env python3
# typedload
# Copyright (C) 2021-2023 Salvo "LtWorf" Tomaselli
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


from subprocess import check_output, DEVNULL, PIPE, Popen
from tempfile import mkdtemp
from shutil import copy, rmtree
import sys
import os
from pathlib import Path


PYVER = '.'.join(str(i) for i in sys.version_info[0:2])


def cpuname() -> str:
    try:
        with open('/proc/cpuinfo', 'rt') as f:
            for i in f:
                if i.startswith('model name'):
                    return i.split(':', 1)[1].strip()
    except Exception:
        pass
    return 'unknown CPU'



def parse_performance(cmd: list[str]) -> tuple[float, float]:
    try:
        out = check_output(cmd, stderr=DEVNULL).replace(b'(', b'').replace(b')', b'').replace(b' ', b'')
        return tuple(float(i) for i in out.split(b',', 1))
    except Exception:
        return -1, -1


def main():
    tests = [
        'dump objects',
        'load list of ints',
        'load list of floats and ints',
        'load list of lists',
        'load big dictionary',
        'load complex dictionary',
        'load list of NamedTuple objects',
        'load list of dataclass objects',
        #'load list of attrs objects',
        'realistic union of objects as namedtuple',
        'fail realistic union of objects as namedtuple',
        'fail load list of floats and ints',
    ]

    extlibs = ['pydantic2', 'apischema']

    outdir = Path('perftest.output')
    if not outdir.exists():
        outdir.mkdir()

    tempdir = mkdtemp()
    for i in ['common'] + tests:
        copy(f'perftest/{i}.py', tempdir)

    tags = check_output(['git', 'tag', '--list'], encoding='ascii').strip().split('\n')
    # Skip minor versions
    tags = [i for i in tags if '-' not in i and ',' not in i and len(i.split('.')) <= 2]
    # Sort by version
    tags.sort(key=lambda i: tuple(int(j) for j in i.split('.')))

    # Keep only recent versions
    tags = tags[-3:]

    # Add current branch and master
    current = check_output(['git', 'branch', '--show-current'], encoding='ascii').strip()
    if current == '':
        pass
    elif current != 'master':
        tags += ['master', current]
    else:
        tags.append('master')

    if 'MOREVERSIONS' in os.environ:
        #TODO add 2.25
        toadd =  [i for i in ['1.20', '2.0', '2.13', '2.15', '2.17', '2.19', '2.21', '2.23'] if i not in tags]
        tags = toadd + tags
    print('Testing tags:', ' '.join(tags))

    plotcmd = []
    maxtime = 0

    for i, t in enumerate(tests):
        print(f'Now running: {t} {i+1}/{len(tests)}')

        test_maxtime = 0

        with open(outdir / f'{t}.dat', 'wt') as f:
            counter = 0

            for library in extlibs:
                print(f'\tRunning test with {library}', end='\t', flush=True)
                library_time, maxduration = parse_performance(['python3', f'{tempdir}/{t}.py', f'--{library}'])
                print(library_time, maxduration)
                test_maxtime = test_maxtime if test_maxtime > maxduration else maxduration
                maxtime = maxtime if maxtime > maxduration else maxduration
                f.write(f'{counter} "{library.replace("_", "-")}" {library_time} {maxduration}\n')
                counter += 1
            for branch in tags:
                print(f'\tRunning test with {branch}', end='\t', flush=True)
                check_output(['git', 'checkout', branch], stderr=DEVNULL)
                typedload_time, maxduration = parse_performance(['python3', f'{tempdir}/{t}.py', '--typedload'])
                print(typedload_time, maxduration)
                f.write(f'{counter} "{branch}" {typedload_time} {maxduration}\n')
                test_maxtime = test_maxtime if test_maxtime > maxduration else maxduration
                maxtime = maxtime if maxtime > maxduration else maxduration
                counter += 1
        with Popen(['gnuplot'], stdin=PIPE, encoding='ascii') as p:
            f = p.stdin
            version = f'python {sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]} {cpuname()}'
            print('set style fill solid 0.2 noborder', file=f)
            print('set ylabel "seconds"', file=f)
            print('set xlabel "package"', file=f)
            print('set boxwidth 0.8', file=f)
            print('set xlabel "x-units" font "Times-Roman,12"', file=f)
            print('set style fill solid 1.0', file=f)
            print(f'set title "typedload performance test {version}"', file=f)
            print(f'set yrange [0:{test_maxtime + test_maxtime * 0.1}]', file=f)
            print('set term svg', file=f)
            print(f'set output "{outdir}/{PYVER}_{t.replace(" ", "_")}.svg"', file=f)
            print(f'plot "{outdir}/{t}.dat" using 1:3:xtic(2) with boxes title "{t}"', file=f)
            f.close()


        plotcmd.append(f'"{t}.dat" using 1:3:4 with filledcurves title "", "" using 1:3:xtic(2) with linespoint title "{t}"')
    rmtree(tempdir)

    gnuplot_script = outdir / 'perf.p'
    with open(gnuplot_script, 'wt') as f:
        print('set style fill transparent solid 0.2 noborder', file=f)
        print('set ylabel "seconds"', file=f)
        print('set xlabel "package"', file=f)
        print(f'set title "typedload performance test {sys.version}"', file=f)
        print(f'set yrange [0:{maxtime}]', file=f)
        print('plot ' + ','.join(plotcmd), file=f)
    print(f'Gnuplot script generated in {gnuplot_script}. You can execute')
    print(f'load "{gnuplot_script}"')
    print(f'inside a gnuplot shell')


if __name__ == '__main__':
    main()
