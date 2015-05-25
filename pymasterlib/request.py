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

import datetime
import time
import random

import pymasterlib as lib
from pymasterlib.constants import *


def load_text(ID):
    return lib.message.load_text("request", ID)


def get_time_limit(activity):
    time_limit = TIME_LIMIT[activity]
    time_deviate = random.uniform(-1, 1)
    if time_deviate > 1:
        time_limit += ((TIME_LIMIT_MAX[activity] - TIME_LIMIT[activity]) *
                       time_deviate)
    elif time_deviate < 1:
        time_limit += ((TIME_LIMIT[activity] - TIME_LIMIT_MIN[activity]) *
                       time_deviate)
    return time_limit


def get_allowed(activity):
    """Return whether or not the activity is allowed."""
    lib.slave.forget()

    if (lib.slave.bedtime is None or
            "night_possible" in ACTIVITIES_DICT[activity].get("flags", [])):
        last_time = None
        for a in lib.slave.activities.setdefault(activity, []):
            if last_time is None or a > last_time:
                last_time = a

        interval = GRANT_INTERVAL.get(activity, 0)
        nchores = len(lib.slave.chores) - len(lib.slave.abandoned_chores)
        interval *= CHORE_BONUS.get(activity, 1) ** max(nchores, 0)
        for i in lib.slave.misdeeds:
            for misdeed in lib.slave.misdeeds[i]:
                penalty = MISDEED_PENALTY.get(i, 1)
                if not misdeed["punished"]:
                    interval *= penalty
                else:
                    interval *= min(penalty, MISDEED_PUNISHED_PENALTY)

        if (len(lib.slave.activities[activity]) < LIMIT.get(activity, 9999) and
                (last_time is None or time.time() >= last_time + interval)):
            return True

    return False


def request(activity):
    """
    Request the activity ``activity`` and return whether permission is
    granted.  Same as get_allowed, but also adds the activity as done.
    """
    if get_allowed(activity):
        lib.slave.add_activity(activity)
        return True
    else:
        return False


def allow_timed(activity, m=None):
    """Allow ``activity`` with a time limit, indicating the message ``m``."""
    time_limit = get_time_limit(activity)
    time_limit_text = lib.message.get_printed_time(time_limit, True)
    if m:
        m = ''.join([m, load_text("time_limit")]).format(time_limit_text)
    else:
        m = load_text("time_limit").format(time_limit_text)
    a = [lib.message.load_text("phrases", "finished")]
    if lib.message.get_interruption(m, time_limit, a) is None:
        lib.message.beep()
        m = load_text("time_up")
        a = lib.message.load_text("phrases", "assent")
        time_passed = lib.message.get_time(m, a)
        if time_passed > ONE_MINUTE:
            lib.message.show(load_text("too_long"))
            for _ in range(0, int(time_passed), int(time_limit)):
                lib.assign.punishment(activity)


def allow(ID, activity, msg):
    script = activity.get("script")
    if script:
        lib.message.show_timed(msg, 5)
        eval(script)()
    elif "time_limit" in activity:
        allow_timed(ID, msg)
    else:
        a = lib.message.load_text("phrases", "thank_you")
        lib.message.show(msg, a)


def deny(ID, activity):
    flags = activity.get("flags", [])
    m = load_text("{}_deny".format(ID))
    if "can_beg" in flags:
        a = [lib.message.load_text("phrases", "assent"),
             load_text("beg_{}".format(ID))]
        if lib.message.get_choice(m, a, 0):
            if request("__beg"):
                if random.randrange(100) < BEG_GAME_CHANCE:
                    m = load_text("beg_{}_accept_game".format(ID))
                    a = lib.message.load_text("phrases", "assent")
                    lib.message.show(m, a)
                    lib.scripts.wait_game("taunt_{}".format(ID))
                    m = load_text("beg_{}_game_win".format(ID))
                    allow(ID, activity, m)
                else:
                    m = load_text("beg_{}_accept".format(ID))
                    allow(ID, activity, m)
            else:
                m = load_text("beg_{}_deny".format(ID))
                a = lib.message.load_text("phrases", "assent")
                lib.message.show(m, a)
    else:
        a = lib.message.load_text("phrases", "assent")
        lib.message.show(m, a)


def what():
    m = load_text("ask_what")
    c = []
    for i, activity in ACTIVITIES:
        c.append(load_text("choice_{}".format(i)))
    c.append(load_text("special_choice_bed"))
    c.append(load_text("special_choice_new_chore"))
    c.append(load_text("special_choice_nothing"))
    choice = lib.message.get_choice(m, c, len(c) - 1)

    if choice < len(ACTIVITIES):
        ID, activity = ACTIVITIES[choice]
        other_ID = activity.get("other_activity")
        script = activity.get("script")
        flags = activity.get("flags", [])
        if other_ID:
            other_activity = ACTIVITIES_DICT[other_ID]
            if get_allowed(ID):
                m = load_text("{}_ask_{}".format(ID, other_ID))
                if lib.message.get_bool(m):
                    if request(other_ID):
                        script = script or other_activity.get("script")
                        lib.slave.add_activity(ID)
                        m = load_text("{}_accept_with_{}".format(ID, other_ID))
                        allow(ID, activity, m)
                    else:
                        m = load_text("{}_deny_{}".format(ID, other_ID))
                        lib.message.show(m)
                else:
                    lib.slave.add_activity(ID)
                    m = load_text("{}_accept_no_{}".format(ID, other_ID))
                    allow(ID, activity, m)
            else:
                lib.slave.rejected.append(time.time())
                deny(ID, activity)
        else:
            if request(ID):
                m = load_text("{}_accept".format(ID))
                allow(ID, activity, m)
            else:
                deny(ID, activity)
    elif choice == len(c) - 3:
        lib.scripts.evening_routine()
    elif choice == len(c) - 2:
        if lib.slave.bedtime is None:
            if lib.slave.queued_chore is None:
                lib.message.show(load_text("chore_assign"))
                lib.assign.chore()
            else:
                lib.message.show(load_text("chore_already_assigned"))
        else:
            lib.message.show(load_text("chore_night_no"))
