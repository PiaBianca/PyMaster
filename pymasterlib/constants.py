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

__all__ = ["DATADIR", "SAVEDIR", "RESET", "RESET_FACTS",

           "STARTUP_DATETIME", "STARTUP_DAY", "STARTUP_TIME",

           "ONE_MINUTE", "ONE_HOUR", "ONE_DAY",

           "MALE", "FEMALE",

           "ACTIVITIES", "ACTIVITIES_DICT",

           "TOO_EARLY", "TOO_LATE", "OATH_FAIL", "BED", "LIE",

           "TIME_LIMIT", "TIME_LIMIT_MIN", "TIME_LIMIT_MAX",

           "ORGASM_ASK_DELAY_MIN", "ORGASM_ASK_DELAY_MAX", "ORGASM_CHANCE",
           "ORGASM_WAIT_CHANCE", "ORGASM_WAIT", "ORGASM_WAIT_MIN",
           "ORGASM_WAIT_MAX",

           "FORGET_TIME_ADJUST", "FORGET_TIME", "ACTIVITY_FORGET_TIME",
           "REJECTED_FORGET_TIME",

           "GRANT_INTERVAL",

           "CHORE_BONUS",

           "MISDEED_PENALTY", "MISDEED_PUNISHED_PENALTY", "REJECTED_PENALTY",

           "CHORE_ALLOW_CHANCE", "PUNISHMENT_ALLOW_CHANCE",

           "LIMIT",

           "BED_GAME_CHANCE", "BEG_GAME_CHANCE", "AGONY_THRESHOLD"]

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data-dir",
                    help="The data directory to use (default ./data/en_US)")
parser.add_argument(
    "-s", "--save-dir",
    help="The save directory to use (default ~/.config/.pymaster)")
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
if args.save_dir:
    SAVEDIR = args.save_dir
else:
    SAVEDIR = os.path.join(os.path.expanduser("~"), ".config", ".pymaster")
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
with open(os.path.join(DATADIR, "restricted_activities.json"), "r") as f:
   ACTIVITIES = json.load(f)

ACTIVITIES_DICT = {}
for i, activity in ACTIVITIES:
    ACTIVITIES_DICT[i] = activity

# Misdeeds
TOO_EARLY = "too_early"
TOO_LATE = "too_late"
OATH_FAIL = "oath_fail"
BED = "bed"
LIE = "lie"

# The target for the effective maximum number of chores; if the slave
# has done this many chores, the oldest is guaranteed to be forgotten by
# the time another chore is assigned, and if there are no misdeeds on
# record, the best possible permission grant outcomes will occur.
CHORES_TARGET = 14

# Forgetfulness
FORGET_TIME_TARGET = CHORES_TARGET * ONE_DAY
FORGET_TIME_ADJUST = 0.9
FORGET_TIME = FORGET_TIME_TARGET * (1 / FORGET_TIME_ADJUST) ** CHORES_TARGET
ACTIVITY_FORGET_TIME = {"__beg": 7 * ONE_DAY}
REJECTED_FORGET_TIME = 2 * ONE_DAY

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
MISDEED_PENALTY = {TOO_EARLY: 1.03,
                   TOO_LATE: 1.03,
                   OATH_FAIL: 1.1,
                   BED: 1.2,
                   LIE: 2}
MISDEED_PUNISHED_PENALTY = 1.005
REJECTED_PENALTY = 1.0025

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
