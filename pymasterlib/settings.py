# PyMaster
# Copyright (C) 2014, 2015 FreedomOfRestriction <FreedomOfRestriction@openmailbox.org>
#
# This program is free software: you can redistribute it and/or modify
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

import os
import json

import pymasterlib as lib
from pymasterlib.constants import *


def save():
    program_settings = {"previous_run": lib.previous_run}
    master_settings = {"name": lib.master.name, "sex": lib.master.sex}
    slave_settings = {"name": lib.slave.name, "sex": lib.slave.sex,
                      "birthday": lib.slave.birthday, "oath": lib.slave.oath,
                      "sick": lib.slave.sick, "bedtime": lib.slave.bedtime,
                      "queued_chore": lib.slave.queued_chore,
                      "chores": lib.slave.chores,
                      "abandoned_chores": lib.slave.abandoned_chores,
                      "activities": lib.slave.activities,
                      "misdeeds": lib.slave.misdeeds,
                      "facts": lib.slave.facts}
    settings = {"program": program_settings, "master": master_settings,
                "slave": slave_settings}

    with open(os.path.join(SAVEDIR, "settings.json"), 'w') as f:
        json.dump(settings, f, indent=4, sort_keys=True)


def load():
    try:
        with open(os.path.join(SAVEDIR, "settings.json"), 'r') as f:
            settings = json.load(f)
    except (IOError, ValueError):
        settings = {}

    s_program = settings.get("program", {})
    lib.previous_run = s_program.get("previous_run")

    s_master = settings.get("master", {})
    lib.master.name = s_master.get("name", "PyMaster")
    lib.master.sex = s_master.get("sex")

    s_slave = settings.get("slave", {})
    lib.slave.name = s_slave.get("name", "Slave")
    lib.slave.sex = s_slave.get("sex")
    lib.slave.birthday = tuple(s_slave.get("birthday", (1, 1)))
    lib.slave.oath = s_slave.get("oath")
    lib.slave.sick = s_slave.get("sick", False)
    lib.slave.bedtime = s_slave.get("bedtime")
    lib.slave.queued_chore = s_slave.get("queued_chore")
    lib.slave.chores = s_slave.get("chores", [])
    lib.slave.abandoned_chores = s_slave.get("abandoned_chores", [])
    lib.slave.activities = s_slave.get("activities", {})
    lib.slave.misdeeds = s_slave.get("misdeeds", {})
    lib.slave.facts = s_slave.get("facts", {})
