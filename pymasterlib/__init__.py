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
import time
import random

from pymasterlib.constants import *
from pymasterlib import (ask, assign, message, parse, request, scripts,
                         settings, tell)


__all__ = ["ask", "assign", "message", "parse", "punish", "scripts", settings,
           "tell"]

previous_run = None


class master:

    name = "Monty"
    sex = None


class slave:

    name = "Slave"
    sex = None
    birthday = STARTUP_DAY[1:]
    oath = None

    bedtime = None
    request_denied = {}
    queued_chore = None
    chores = []
    abandoned_chores = []
    activities = {}
    misdeeds = {}
    rejected = []
    facts = {}

    @classmethod
    def forget(cls):
        def get_forget_time():
            memory_num = len(cls.chores)
            for i in cls.misdeeds:
                memory_num += len(cls.misdeeds[i])

            return FORGET_TIME * (FORGET_TIME_ADJUST ** memory_num)

        forgotten = []
        for i in range(len(cls.chores)):
            if time.time() >= cls.chores[i]["time"] + get_forget_time():
                forgotten.append(i)
        for i in sorted(forgotten, reverse=True):
            del cls.chores[i]

        invalid = []
        for i in cls.misdeeds:
            if i not in MISDEED_PENALTY:
                print("Warning: Deleting invalid misdeed \"{}\"".format(i))
                invalid.append(i)
                continue

            forgotten = []
            for j in range(len(cls.misdeeds[i])):
                if time.time() >= cls.misdeeds[i][j]["time"] + get_forget_time():
                    forgotten.append(j)
            for j in sorted(forgotten, reverse=True):
                md = cls.misdeeds[i][j]
                punishment = md["punishment"]
                if punishment is not None and not md["punished"]:
                    t = punishment.get("time")
                    for activity in punishment.get("activities", []):
                        try:
                            cls.activities[parse.python(activity)].remove(t)
                        except (KeyError, ValueError):
                            print("Warning: Didn't find activity \"{}\" at the time of this punishment.".format(activity))
                del cls.misdeeds[i][j]

        for i in invalid:
            del cls.misdeeds[i]

        invalid = []
        for i in cls.activities:
            try:
                forget_time = ACTIVITY_FORGET_TIME[i]
            except KeyError:
                print("Warning: Deleting invalid activity \"{}\"".format(i))
                invalid.append(i)
                continue

            forgotten = []
            for j in range(len(cls.activities[i])):
                if time.time() >= cls.activities[i][j] + forget_time:
                    forgotten.append(j)
            for j in sorted(forgotten, reverse=True):
                del cls.activities[i][j]

        for i in invalid:
            del cls.activities[i]

        forgotten = []
        for i in range(len(cls.rejected)):
            if time.time() >= cls.rejected[i] + REJECTED_FORGET_TIME:
                forgotten.append(i)
        for i in sorted(forgotten, reverse=True):
            del cls.rejected[i]

        forgotten = []
        for i in cls.facts:
            forget = cls.facts[i]["forget"]
            if forget is not None and time.time() >= forget:
                forgotten.append(i)
        for i in forgotten:
            del cls.facts[i]

    @classmethod
    def add_activity(cls, activity):
        cls.activities.setdefault(activity, []).append(time.time())

    @classmethod
    def add_misdeed(cls, activity, punishment=None):
        misdeed = {"time": time.time(), "punishment": punishment,
                   "punished": False}
        cls.misdeeds.setdefault(activity, []).append(misdeed)

    @classmethod
    def get_fact(cls, fact):
        cls.forget()
        with open(os.path.join(DATADIR, "facts.json"), 'r') as f:
            facts = json.load(f)

        if fact not in cls.facts:
            fdict = facts.get(fact, {})
            firstcheck = fdict.get("firstcheck")
            value = parse.python(firstcheck) if firstcheck else None
            if "forget" in fdict:
                forget = time.time() + parse.python(fdict["forget"])
            else:
                forget = None

            cls.facts[fact] = {"value": value, "forget": forget}

        return cls.facts[fact]["value"]
