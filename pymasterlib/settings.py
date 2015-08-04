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
import sys
import json

import pymasterlib as lib
from pymasterlib.constants import *


def save():
    program_settings = {"previous_run": lib.previous_run,
                        "data_dirs": lib.data_dirs}
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
    lib.data_dirs = s_program.get("data_dirs", [])

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

    if DATADIRS:
        lib.data_dirs = DATADIRS
    elif not lib.data_dirs:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
                                                "data"))
        dl = os.listdir(base_dir)
        dirs = []
        for d in dl:
            if os.path.isdir(os.path.join(base_dir, d)):
                dirs.append(d)

        if len(dirs) > 1:
            m = "Language selection"
            i = lib.message.get_choice(m, dirs)
            lib.data_dirs = [os.path.abspath(os.path.join(base_dir,
                                                          dirs.pop(i)))]
        elif dirs:
            lib.data_dirs = [os.path.abspath(os.path.join(base_dir,
                                                          dirs.pop(0)))]
        else:
            m = "Error: Could not find the PyMaster data directories. Please specify the directory manually with the -d option."
            lib.message.show(m)
            sys.exit()

        # Fall back to English
        for d in dirs:
            if d.startswith("en"):
                lib.data_dirs.append(os.path.join(base_dir, d))

    lib.data_dir = lib.data_dirs[0]

    # TODO: Recommend a default set of extensions
    lib.ext_dirs = EXTDIRS

    # Restricted activities
    # This is a list of pairs instead of a dictionary because their
    # order matters; the user needs to be shown the activities in
    # exactly the same order every time, and this order should be
    # controlled by the JSON file (as opposed to e.g. alphabetical
    # sorting) so that it can be an order that makes logical sense.
    for d in lib.ext_dirs[::-1] + [lib.data_dir]:
        fname = os.path.join(d, "restricted_activities.json")
        try:
            with open(fname, 'r') as f:
                lib.activities = json.load(f)
                break
        except OSError:
            continue
    else:
        lib.activities = []

    lib.activities_dict = {}
    for i, activity in lib.activities:
        lib.activities_dict[i] = activity

    # Misdeeds
    # See the above explanation for why this is a list of pairs,
    # rather than a dictionary.
    for d in lib.ext_dirs[::-1] + [lib.data_dir]:
        fname = os.path.join(d, "misdeeds.json")
        try:
            with open(fname, 'r') as f:
                lib.misdeeds = json.load(f)
                break
        except OSError:
            continue
    else:
        lib.misdeeds = []

    lib.misdeeds_dict = {}
    for i, misdeed in lib.misdeeds:
        lib.misdeeds_dict[i] = misdeed
