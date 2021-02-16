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


from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, NamedTuple, Optional, Set, Tuple, Union
import unittest

from typedload import dataloader, load, dump, typechecks

class Firewall(NamedTuple):
    open_ports: List[int]


class Networking(NamedTuple):
    nic: Optional[str]
    firewall: Firewall


class Remote(NamedTuple):
    networking: Networking


class Config(NamedTuple):
    remote: Optional[Remote]

class TestExceptionsStr(unittest.TestCase):

    def test_exceptions_str(self):
        incorrect = [
            {'remote': {'networking': {'nic': "eth0", "firewall": {"open_ports":[1,2,3, 'a']}}}},
            {'remote': {'networking': {'nic': "eth0", "firewall": {"closed_ports": [], "open_ports":[1,2,3]}}}},
            {'remote': {'networking': {'nic': "eth0", "firewall": {"open_ports":[2,3]}}}},
            {'romote': {'networking': {'nic': "eth0", "firewall": {"open_ports":[2,3]}}}},
            {'remote': {'nitworking': {'nic': "eth0", "firewall": {"open_ports":[2,3]}}}},
        ]
        for i in incorrect:
            try:
                load(i, Config, basiccast=False, failonextra=True)
            except Exception as e:
                str(e)
