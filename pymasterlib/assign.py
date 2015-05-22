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
import datetime
import time
import random
import json

import pymasterlib as lib
from pymasterlib.constants import *

__all__ = ["chore", "punishment"]


def load_text(ID):
    return lib.message.load_text("assign", ID)


def chore():
    """Assign a random chore to the slave."""
    lib.slave.forget()

    with open(os.path.join(DATADIR, "chores.json"), 'r') as f:
        chores = json.load(f)

    allow_all = (random.randrange(100) < CHORE_ALLOW_CHANCE)

    while chores:
        keys = list(chores.keys())
        i = keys[random.randrange(len(keys))]
        requires = chores[i].setdefault("requires")
        text_choices = chores[i].setdefault("text", [])

        if text_choices:
            allowed = True
            if not allow_all:
                for activity in chores[i].setdefault("activities", []):
                    if not lib.request.get_allowed(activity):
                        allowed = False
                        break

            if allowed and (not requires or eval(requires)):
                text = lib.parse.python_tag(random.choice(text_choices))
                chores[i]["text"] = text
                t = time.time()
                chores[i]["time"] = t
                lib.slave.queued_chore = chores[i]
                for activity in chores[i].setdefault("activities", []):
                    lib.slave.activities.setdefault(activity, []).append(t)
                lib.message.show(text)
                break

        del chores[i]
    else:
        lib.message.show(load_text("no_chores"))


def punishment(misdeed):
    """Assign and return a random punishment for the misdeed indicated."""
    lib.slave.forget()

    with open(os.path.join(DATADIR, "punishments.json"), 'r') as f:
        punishments = json.load(f)

    with open(os.path.join(DATADIR, "punishments_list.json"), 'r') as f:
        punishments_list = json.load(f)

    allow_all = (random.randrange(100) < PUNISHMENT_ALLOW_CHANCE)
    punishment_choices = punishments_list.setdefault(misdeed, [])

    while punishment_choices:
        index = random.randrange(len(punishment_choices))
        i = punishment_choices[index]
        if i in punishments:
            requires = punishments[i].setdefault("requires")
            if not requires or eval(requires):
                allowed = True
                if not allow_all:
                    for activity in punishments[i].setdefault("activities", []):
                        if not lib.request.get_allowed(activity):
                            allowed = False
                            break

                text_choices = punishments[i].setdefault("text", [])

                if allowed and text_choices:
                    text = lib.parse.python_tag(random.choice(text_choices))
                    punishments[i]["text"] = text
                    t = time.time()
                    punishments[i]["time"] = t
                    lib.slave.add_misdeed(misdeed, punishments[i])
                    for activity in punishments[i].setdefault("activities", []):
                        lib.slave.activities.setdefault(activity, []).append(t)
                    m = punishments[i]["text"]
                    a = lib.message.load_text("phrases", "assent")
                    lib.message.show(m, a)
                    break

        del punishment_choices[index]
    else:
        # Can't give a punishment
        lib.slave.add_misdeed(misdeed)

    return None
