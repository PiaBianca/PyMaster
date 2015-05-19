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

import time
import random

import pymasterlib as lib
from pymasterlib.constants import *


def load_text(ID):
    return lib.message.load_text("tell", ID)


def what():
    m = load_text("ask_what")
    c = [load_text("choice_completed_chore"),
         load_text("choice_completed_punishment"), load_text("choice_naughty"),
         load_text("choice_lied"), load_text("choice_nothing")]
    choice = lib.message.get_choice(m, c, len(c) - 1)

    if choice == 0:
        completed_chore()
    elif choice == 1:
        completed_punishment()
    elif choice == 2:
        broke_rule()
    elif choice == 3:
        lied()


def completed_chore():
    if lib.slave.queued_chore is not None:
        m = '\n'.join([load_text("chore_check"),
                       lib.slave.queued_chore["text"]])
        if lib.message.get_bool(m):
            lib.slave.queued_chore["time"] = time.time()
            lib.slave.chores.append(lib.slave.queued_chore)
            lib.slave.queued_chore = None
            lib.message.show(load_text("chore_done"))
    else:
        lib.message.show(load_text("no_chore"))

    lib.settings.save()


def completed_punishment():
    lib.slave.forget()

    punishments = []
    punishment_text = []
    for i in lib.slave.misdeeds:
        for j in range(len(lib.slave.misdeeds[i])):
            if (not lib.slave.misdeeds[i][j]["punished"] and
                    lib.slave.misdeeds[i][j]["punishment"] is not None):
                punishments.append((i, j))
                punishment_text.append(
                    lib.slave.misdeeds[i][j]["punishment"]["text"])

    if punishments:
        if len(punishments) == 1:
            i = 0
        else:
            i = lib.message.get_choice("Which one?", punishment_text)

        m = '\n'.join([load_text("punishment_check"), punishment_text[i]])
        if lib.message.get_bool(m):
            a, b = punishments[i]
            lib.slave.misdeeds[a][b]["punished"] = True
            lib.message.show(load_text("punishment_done"))
    else:
        lib.message.show(load_text("no_punishment"))

    lib.settings.save()


def broke_rule():
    m = load_text("ask_what_naughty")
    c = []
    for i, activity in ACTIVITIES:
        c.append(load_text("choice_naughty_{}".format(i)))
    c.append(load_text("choice_special_naughty_bed"))
    c.append(load_text("choice_special_naughty_nothing"))
    choice = lib.message.get_choice(m, c, len(c) - 1)

    if choice < len(ACTIVITIES):
        ID, activity = ACTIVITIES[choice]
        m = load_text("response_naughty_{}".format(ID))
        lib.message.show(m)
        lib.slave.add_activity(ID)
        lib.assign.punishment(ID)
    elif choice == len(c) - 2:
        skipped_evening_routine()


def skipped_evening_routine():
    lib.message.show(load_text("response_naughty_bed"))
    lib.assign.punishment(BED)


def lied():
    lib.message.show(load_text("response_lied"))
    lib.assign.punishment(LIE)
