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

__all__ = ["DATADIRS", "SAVEDIR", "EXTDIRS", "RESET", "RESET_FACTS",

           "STARTUP_DATETIME", "STARTUP_DAY", "STARTUP_TIME",

           "ONE_MINUTE", "ONE_HOUR", "ONE_DAY",

           "MALE", "FEMALE",

           "ORGASM_ASK_DELAY_MIN", "ORGASM_ASK_DELAY_MAX", "ORGASM_CHANCE",
           "ORGASM_WAIT_CHANCE", "ORGASM_WAIT", "ORGASM_WAIT_MIN",
           "ORGASM_WAIT_MAX", "ORGASM_TIME_LIMIT", "ORGASM_TIME_LIMIT_MIN",
           "ORGASM_TIME_LIMIT_MAX",

           "CHORES_TARGET",

           "FORGET_TIME", "FORGET_TIME_TARGET", "FORGET_TIME_ADJUST",
           "FORGET_TIME_NEGATIVE_ADJUST",

           "SPECIAL_ACTIVITIES", "MISDEED_PUNISHED_PENALTY",

           "BEG_GAME_CHANCE", "AGONY_THRESHOLD"]

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d", "--data-dirs", nargs="*",
    help="The data directories to use (directories after the first one are only used for text which is not found in the first directory, in order of preference)")
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

if args.data_dirs:
    DATADIRS = args.data_dirs
else:
    DATADIRS = []

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

# Special activities and misdeeds
SPECIAL_ACTIVITIES = ["__beg", "oath_fail", "too_early", "too_late"]
MISDEED_PUNISHED_PENALTY = 1.005

# Orgasm stuff
ORGASM_ASK_DELAY_MIN = 30
ORGASM_ASK_DELAY_MAX = 5 * ONE_MINUTE
ORGASM_CHANCE = 7
ORGASM_WAIT_CHANCE = 60
ORGASM_WAIT = ONE_MINUTE
ORGASM_WAIT_MIN = 30
ORGASM_WAIT_MAX = ONE_MINUTE * 2
ORGASM_TIME_LIMIT = 60
ORGASM_TIME_LIMIT_MIN = 45
ORGASM_TIME_LIMIT_MAX = 90

# Games
BEG_GAME_CHANCE = 95
AGONY_THRESHOLD = 5 * ONE_MINUTE
