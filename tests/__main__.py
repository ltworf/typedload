# typedload
# Copyright (C) 2018-2019 Salvo "LtWorf" Tomaselli
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


import unittest
import sys

print('Running tests using %s' % sys.version)
if sys.version_info.major != 3 or sys.version_info.minor < 5:
    raise Exception('Only version 3.5 and above supported')

if sys.version_info.minor > 5:
    from .test_dataloader import *
    from .test_datadumper import *
    from .test_dumpload import *
if sys.version_info.minor >= 7:
    from .test_dataclass import *
from .test_legacytuples_dataloader import *
from .test_typechecks import *

# Run tests for the attr plugin only if it is loaded
try:
    import attr
    attr_module = True
except ImportError:
    attr_module = False

if attr_module:
    from .test_attrload import *

if sys.version_info.minor >= 7:
    from .test_fa_dataloader import *
    from .test_fa_datadumper import *
    from .test_fa_dumpload import *
    from .test_fa_dataclass import *
    from .test_fa_legacytuples_dataloader import *
    from .test_fa_typechecks import *
    if attr_module:
        from .test_fa_attrload import *

if __name__ == '__main__':
    unittest.main()
