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

    def assign_chore(c, i, text_choices):
        c["id"] = i
        text = lib.parse.python_tag(random.choice(text_choices))
        c["text"] = text
        t = time.time()
        c["time"] = t
        lib.slave.queued_chore = c
        for activity in c.setdefault("activities", []):
            lib.slave.activities.setdefault(activity, []).append(t)
        lib.message.show(text)

    chores = {}
    for d in [DATADIR] + EXTDIRS:
        fname = os.path.join(d, "chores.json")
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                nchores = json.load(f)
            for i in nchores:
                chores[i] = nchores[i]

    backup_chores = {}

    allow_all = (random.randrange(100) < CHORE_ALLOW_CHANCE)

    while chores:
        keys = list(chores.keys())
        i = random.choice(keys)
        requires = chores[i].setdefault("requires")
        text_choices = chores[i].setdefault("text", [])

        if text_choices:
            allowed = True
            if not allow_all:
                for activity in chores[i].setdefault("activities", []):
                    if not lib.request.get_allowed(activity):
                        allowed = False
                        break

            if allowed:
                repeat = False
                for done_chore in lib.slave.chores:
                    if done_chore.get("id") == i:
                        repeat = True
                        break

                if not repeat:
                    if not requires or eval(requires):
                        assign_chore(chores[i], i, text_choices)
                        break
                else:
                    backup_chores[i] = chores[i]

        del chores[i]
    else:
        while backup_chores:
            keys = list(backup_chores.keys())
            i = random.choice(keys)
            requires = backup_chores[i].setdefault("requires")
            text_choices = backup_chores[i].setdefault("text", [])
            if text_choices and (not requires or eval(requires)):
                assign_chore(backup_chores[i], i, text_choices)
            
        lib.message.show(load_text("no_chores"))


def punishment(misdeed):
    """Assign and return a random punishment for the misdeed indicated."""
    lib.slave.forget()

    punishments = {}
    for d in [DATADIR] + EXTDIRS:
        fname = os.path.join(d, "punishments.json")
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                upunishments = json.load(f)
            for i in upunishments:
                punishments[i] = upunishments[i]

    punishments_list = {}
    for d in [DATADIR] + EXTDIRS:
        fname = os.path.join(d, "punishments_list.json")
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                upunishments_list = json.load(f)
            for i in upunishments_list:
                if i in punishments_list:
                    punishments_list[i].extend(upunishments_list[i])
                else:
                    punishments_list[i] = upunishments_list[i]

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
