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

__all__ = ["chore", "night_chore", "punishment"]


def load_text(ID):
    return lib.message.load_text("assign", ID)


def _assign_chore(c, i, text_choices):
    c["id"] = i
    text = lib.parse.python_tag(random.choice(text_choices))
    c["text"] = text
    t = time.time()
    c["time"] = t
    lib.slave.queued_chore = c
    for activity in c.setdefault("activities", []):
        lib.slave.activities.setdefault(activity, []).append(t)
    lib.message.show(text)


def chore():
    """Assign a random chore to the slave."""
    lib.slave.forget()

    chores = {}
    for d in [lib.data_dir] + lib.ext_dirs:
        fname = os.path.join(d, "chores.json")
        try:
            with open(fname, 'r') as f:
                nchores = json.load(f)
            for i in nchores:
                chores[i] = nchores[i]
        except OSError:
            continue

    backup_chores = {}

    while chores:
        keys = list(chores.keys())
        i = random.choice(keys)
        requires = chores[i].setdefault("requires")
        text_choices = chores[i].setdefault("text", [])

        if text_choices:
            allowed = True
            for activity in chores[i].setdefault("activities", []):
                allow_chance = lib.activities_dict.get(activity, {}).get(
                    "chore_allow_chance", 0)
                if (not lib.request.get_allowed(activity) and
                        random.random() >= allow_chance):
                    allowed = False
                    break

            if allowed:
                repeat = False
                for done_chore in lib.slave.chores:
                    did = done_chore.get("id")
                    if did == i or did in chores[i].get("similar", []):
                        repeat = True
                        break

                if not repeat:
                    if not requires or eval(requires):
                        _assign_chore(chores[i], i, text_choices)
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
                _assign_chore(backup_chores[i], i, text_choices)
                break
            del backup_chores[i]
        else:
            lib.message.show(load_text("no_chores"))


def night_chore():
    """
    Assign a random night chore to the slave.  Night chores are the same
    as regular chores techically, but are separated so whether the slave
    is asleep can be taken into account.
    """
    lib.slave.forget()

    chores = {}
    for d in [lib.data_dir] + lib.ext_dirs:
        fname = os.path.join(d, "night_chores.json")
        try:
            with open(fname, 'r') as f:
                nchores = json.load(f)
            for i in nchores:
                chores[i] = nchores[i]
        except OSError:
            continue

    while chores:
        keys = list(chores.keys())
        i = random.choice(keys)
        requires = chores[i].setdefault("requires")
        text_choices = chores[i].setdefault("text", [])

        if text_choices:
            allowed = True
            for activity in chores[i].setdefault("activities", []):
                allow_chance = lib.activities_dict.get(activity, {}).get(
                    "chore_allow_chance", 0)
                if (not lib.request.get_allowed(activity) and
                        random.random() >= allow_chance):
                    allowed = False
                    break

            if allowed and (not requires or eval(requires)):
                _assign_chore(chores[i], i, text_choices)
                break

        del chores[i]
    else:
        lib.message.show(load_text("no_chores"))


def routine(i):
    """
    Assign the indicated routine to the slave.  Routines are to be done
    immediately when assigned, for a set amount of time.  They cannot be
    skipped; attempting to do so by pressing Ctrl+C will only postpone
    them.
    """
    r = lib.routines_dict.get(i, {})
    time_min = eval(r.get("time_min", "0"))
    time_max = eval(r.get("time_max", "0"))
    time_ = random.uniform(time_min, time_max)
    script = r.get("script")

    if i not in lib.slave.routine_skips:
        if script:
            eval(script)()
        else:
            m = load_text("routine_{}_assign".format(i))
            lib.message.show_timed(m, time_)
            lib.slave.add_routine(i)
            lib.message.beep()
            m = load_text("routine_{}_end".format(i))
            lib.message.show(m, lib.message.load_text("phrases", "thank_you"))
    else:
        lib.slave.routine_skips.discard(i)
        lib.slave.add_routine(i)


def punishment(misdeed):
    """Assign and return a random punishment for the misdeed indicated."""
    lib.slave.forget()

    punishments = {}
    for d in [lib.data_dir] + lib.ext_dirs:
        fname = os.path.join(d, "punishments.json")
        try:
            with open(fname, 'r') as f:
                upunishments = json.load(f)
            for i in upunishments:
                punishments[i] = upunishments[i]
        except OSError:
            continue

    punishments_list = {}
    for d in [lib.data_dir] + lib.ext_dirs:
        fname = os.path.join(d, "punishments_list.json")
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                upunishments_list = json.load(f)
            for i in upunishments_list:
                if i in punishments_list:
                    punishments_list[i].extend(upunishments_list[i])
                else:
                    punishments_list[i] = upunishments_list[i]

    punishment_choices = punishments_list.setdefault(misdeed, [])

    while punishment_choices:
        index = random.randrange(len(punishment_choices))
        i = punishment_choices[index]
        if i in punishments:
            requires = punishments[i].setdefault("requires")
            if not requires or eval(requires):
                allowed = True
                for activity in punishments[i].setdefault("activities", []):
                    allow_chance = lib.activities_dict.get(activity, {}).get(
                        "chore_allow_chance", 0)
                    if (not lib.request.get_allowed(activity) and
                            random.random() >= allow_chance):
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
