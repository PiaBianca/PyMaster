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

import sys
import os
import datetime
import time
import argparse
import json

__all__ = ["DATADIR", "SAVEDIR", "EXTDIRS", "RESET", "RESET_FACTS",

           "STARTUP_DATETIME", "STARTUP_DAY", "STARTUP_TIME",

           "ONE_MINUTE", "ONE_HOUR", "ONE_DAY",

           "MALE", "FEMALE",

           "ACTIVITIES", "ACTIVITIES_DICT",

           "MISDEEDS", "MISDEEDS_DICT",

           "TIME_LIMIT", "TIME_LIMIT_MIN", "TIME_LIMIT_MAX",

           "ORGASM_ASK_DELAY_MIN", "ORGASM_ASK_DELAY_MAX", "ORGASM_CHANCE",
           "ORGASM_WAIT_CHANCE", "ORGASM_WAIT", "ORGASM_WAIT_MIN",
           "ORGASM_WAIT_MAX",

           "CHORES_TARGET",

           "FORGET_TIME", "FORGET_TIME_TARGET", "FORGET_TIME_ADJUST",
           "FORGET_TIME_NEGATIVE_ADJUST", "ACTIVITY_FORGET_TIME",

           "GRANT_INTERVAL",

           "CHORE_BONUS",

           "MISDEED_PENALTY", "MISDEED_PUNISHED_PENALTY",

           "CHORE_ALLOW_CHANCE", "PUNISHMENT_ALLOW_CHANCE",

           "LIMIT",

           "BEG_GAME_CHANCE", "AGONY_THRESHOLD"]

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data-dir",
                    help="The data directory to use (default ./data/en_US)")
parser.add_argument(
    "-s", "--save-dir",
    help="The save directory to use (default ~/.config/.pymaster)")
parser.add_argument(
    "-e", "--ext-dirs", nargs="*",
    help="Directories to search for extensions in.")
parser.add_argument(
    "--reset",
    help="Reset PyMaster to its original state, deleting all user data",
    action="store_true")
parser.add_argument(
    "--reset-facts",
    help="Reset your master or mistress's memories of facts about you, such as equipment and abilities you have, so that you will be asked about them again",
    action="store_true")
args = parser.parse_args()

if args.data_dir:
    DATADIR = args.data_dir
else:
    DATADIR = os.path.join(os.path.dirname(sys.argv[0]), "data", "en_US")
DATADIR = os.path.abspath(DATADIR)

if args.save_dir:
    SAVEDIR = args.save_dir
else:
    SAVEDIR = os.path.join(os.path.expanduser("~"), ".config", ".pymaster")
SAVEDIR = os.path.abspath(SAVEDIR)

if args.ext_dirs:
    EXTDIRS = args.ext_dirs
else:
    EXTDIRS = []

RESET = args.reset
RESET_FACTS = args.reset_facts

STARTUP_DATETIME = datetime.datetime.now()
STARTUP_DAY = (STARTUP_DATETIME.year, STARTUP_DATETIME.month,
               STARTUP_DATETIME.day)
STARTUP_TIME = time.time()

# Times in seconds
ONE_MINUTE = 60
ONE_HOUR = 60 * ONE_MINUTE
ONE_DAY = 24 * ONE_HOUR

# Sexes
MALE = "m"
FEMALE = "f"

# Activities
# This is a list of pairs instead of a dictionary because their order
# matters; the user needs to be shown the activities in exactly the same
# order every time, and this order should be controlled by the JSON
# file (as opposed to e.g. alphabetical sorting) so that it can be an
# order that makes logical sense.
ACTIVITIES = []
for d in [DATADIR] + EXTDIRS:
    fname = os.path.join(d, "restricted_activities.json")
    if os.path.isfile(fname):
        with open(fname, "r") as f:
            ACTIVITIES.extend(json.load(f))

ACTIVITIES_DICT = {}
for i, activity in ACTIVITIES:
    ACTIVITIES_DICT[i] = activity

# Misdeeds
# See the above explanation for why this is a list of pairs, rather than
# a dictionary.
MISDEEDS = []
for d in [DATADIR] + EXTDIRS:
    fname = os.path.join(d, "misdeeds.json")
    if os.path.isfile(fname):
        with open(fname, "r") as f:
            MISDEEDS.extend(json.load(f))

MISDEEDS_DICT = {}
for i, misdeed in MISDEEDS:
    MISDEEDS_DICT[i] = misdeed

# The target for the best-case number of chores; if the slave has done
# this many chores, they are forgotten at an interval of
# FORGET_TIME_TARGET, and if there are no misdeeds on  record,
# restricted activities are granted at an interval of the respective
# GRANT_INTERVAL_GOOD.
CHORES_TARGET = 14

# The effective maximum number of chores; if the number of chores is
# greater than CHORES_TARGET, and the number of chores + misdeeds is
# CHORES_MAX + 1, the forget time becomes 0 (ensuring that the oldest
# chore is forgotten).  Note that the effective maximum number of chores
# is reduced if any misdeeds are in memory, and can be as low as
# CHORES_TARGET.
CHORES_MAX = 17

# Forgetfulness
FORGET_TIME_TARGET = 14 * ONE_DAY
FORGET_TIME = 28 * ONE_DAY
FORGET_TIME_ADJUST = (FORGET_TIME - FORGET_TIME_TARGET) / (CHORES_TARGET ** 3)
FORGET_TIME_NEGATIVE_ADJUST = (-FORGET_TIME_TARGET /
                               ((CHORES_TARGET - (CHORES_MAX + 1)) ** 3))
ACTIVITY_FORGET_TIME = {"__beg": 7 * ONE_DAY}

# Required wait for permission (adjusted by chores and misdeeds)
GRANT_INTERVAL = {"__beg": 1}
GRANT_INTERVAL_GOOD = {"__beg": 1}

# Limits
LIMIT = {"__beg": 2}

# Time limits
TIME_LIMIT = {"__orgasm": 60}
TIME_LIMIT_MIN = {"__orgasm": 45}
TIME_LIMIT_MAX = {"__orgasm": 90}

# Penalties
MISDEED_PENALTY = {"too_early": 1.03,
                   "too_late": 1.03,
                   "oath_fail": 1.1}
MISDEED_PUNISHED_PENALTY = 1.005

# Add restricted activities
for i, activity in ACTIVITIES:
    ACTIVITY_FORGET_TIME[i] = eval(activity.get("forget_time", "1"))
    if "interval" in activity:
        GRANT_INTERVAL[i] = eval(activity["interval"])
    if "interval_good" in activity:
        GRANT_INTERVAL_GOOD[i] = eval(activity["interval_good"])
    if "limit" in activity:
        LIMIT[i] = activity["limit"]
    if "time_limit" in activity:
        TIME_LIMIT[i] = eval(activity["time_limit"])
        TIME_LIMIT_MIN[i] = eval(activity.get("time_limit_min",
                                              activity["time_limit"]))
        TIME_LIMIT_MAX[i] = eval(activity.get("time_limit_max",
                                              activity["time_limit"]))
    MISDEED_PENALTY[i] = activity.get("penalty", 1)

# Add misdeeds
for i, misdeed in MISDEEDS:
    MISDEED_PENALTY[i] = misdeed.get("penalty", 1)

# Interval adjustments
CHORE_BONUS = {}
for i in GRANT_INTERVAL:
    CHORE_BONUS[i] = 1 / ((GRANT_INTERVAL[i] / GRANT_INTERVAL_GOOD[i]) **
                          (1 / CHORES_TARGET))

# Orgasm stuff
ORGASM_ASK_DELAY_MIN = 30
ORGASM_ASK_DELAY_MAX = 5 * ONE_MINUTE
ORGASM_CHANCE = 7
ORGASM_WAIT_CHANCE = 60
ORGASM_WAIT = ONE_MINUTE
ORGASM_WAIT_MIN = 30
ORGASM_WAIT_MAX = ONE_MINUTE * 2

# Chance of not allowed activities being allowed anyway
CHORE_ALLOW_CHANCE = 5
PUNISHMENT_ALLOW_CHANCE = 2

# Games
BEG_GAME_CHANCE = 95
AGONY_THRESHOLD = 5 * ONE_MINUTE
