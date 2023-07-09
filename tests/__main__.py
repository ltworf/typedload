# typedload
# Copyright (C) 2018-2023 Salvo "LtWorf" Tomaselli
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
if sys.version_info.major != 3 or sys.version_info.minor < 8:
    raise Exception('Only version 3.5 and above supported')

from .test_dataloader import *
from .test_datadumper import *
from .test_dumpload import *
from .test_exceptions import *
from .test_dataclass import *
from .test_deferred import *
from .test_legacytuples_dataloader import *
from .test_typechecks import *
from .test_datetime import *
from .test_literal import *
from .test_typeddict import *

if sys.version_info.minor >= 10:
    from .test_orunion import *

# Run tests for the attr plugin only if it is loaded
try:
    import attr
    attr_module = True
except ImportError:
    attr_module = False

if attr_module:
    from .test_attrload import *

if __name__ == '__main__':
    unittest.main()
