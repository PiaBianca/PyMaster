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
import math
import time
import json
import random

import pymasterlib as lib
from pymasterlib.constants import *

__all__ = ["init", "get_printed_time", "show", "show_timed", "get_time",
           "get_interrupted", "get_choice", "get_bool", "get_int",
           "get_string", "beep"]


def _insert_newlines(text, linesize=72):
    # Insert newlines into the text so that each line is linesize or
    # fewer characters long.
    lines = text.splitlines()
    new_lines = []

    for line in lines:
        new_line = ""
        words = line.split()
        for word in words:
            if len(new_line) + len(word) + 1 <= linesize:
                new_line = ' '.join([new_line, word])
            else:
                new_lines.append(new_line.strip())
                new_line = word

        new_lines.append(new_line.strip())

    return '\n'.join(new_lines)


def init():
    """
    Initialize the message module.  Can involve things like opening a
    main window.  Should be called before any of this module is used.
    """


def get_printed_time(time_, round_down=False):
    """
    Get a string properly representing the given time.

    The string returned is rounded up to the nearest minute.  For
    example, 124 seconds will result in "3 minutes".

    If ``round_down`` is True, it will be rounded *down* to the nearest
    minute instead of up. For example, 112 seconds will result in
    "1 minute".
    """
    if round_down:
        minutes = math.floor(time_ / 60)
    else:
        minutes = math.ceil(time_ / 60)
    hours = int(minutes / 60)
    minutes %= 60

    if hours == 1:
        hours_text = load_text("phrases", "time_1_hour")
    else:
        hours_text = load_text("phrases", "time_hours").format(hours)

    if minutes == 1:
        minutes_text = load_text("phrases", "time_1_minute")
    else:
        minutes_text = load_text("phrases", "time_minutes").format(minutes)
    
    if hours > 0:
        if minutes > 0:
            join_text = load_text("phrases", "time_hours_and_minutes")
            return join_text.format(hours=hours_text, minutes=minutes_text)
        else:
            return hours_text
    else:
        return minutes_text


def load_text(section, ID):
    """
    Return a choice of text with the requested ID in the requested
    section.  If it does not exist, return ID instead.
    """
    dirnames = lib.ext_dirs[::-1] + lib.data_dirs
    for dirname in dirnames:
        fname = os.path.join(dirname, "text_{}.json".format(section))
        if os.path.isfile(fname):
            with open(fname, 'r') as f:
                texts = json.load(f)

            if ID in texts and texts[ID]:
                return lib.parse.python_tag(random.choice(texts[ID]))
    else:
        return ID


def show(message, answer=None):
    """
    Show a message to the slave.

    If ``answer`` is not None, it will be used as the slave's response.
    """
    if answer is None:
        print(_insert_newlines(message), end=" ")
        input("[...]")
    else:
        print(_insert_newlines(message))
        input("[{}]".format(answer))


def show_timed(message, time_):
    """Show a message for a set amount of time (in seconds)."""
    print(_insert_newlines(message))
    time.sleep(time_)


def get_time(message, answer=None):
    """Like ``show``, but return the time the slave takes to answer."""
    start = time.time()
    show(message, answer)
    end = time.time()
    return end - start


def get_interruption(message, wait, answers=None):
    """
    Like ``show_timed``, but can be interrupted.

    ``answers`` is a list of things the slave can say for the
    interruption, or ``None`` for the wait to just be skipped without
    the slave saying anything.

    Return the index of the interruption (answer) used, or ``None`` if
    there was no interruption.
    """
    if answers:
        if len(answers) == 1:
            m = 'Press CTRL+C to say: "{}"'.format(answers[0])
        else:
            a = '", "'.join(answers)
            m = 'Press CTRL+C to say one of the following: "{}"'.format(a)
        lines = _insert_newlines(m, 60).splitlines()
        for i in range(len(lines)):
            lines[i] = ''.join([lines[i], " " * (60 - len(lines[i]))])
            lines[i] = ''.join(["::    ", lines[i], "    ::"])
        infotext = '\n'.join(lines)
    else:
        infotext = "::    Press CTRL+C to skip the wait    ::"

    print(_insert_newlines(message))
    print(infotext)
    try:
        time.sleep(max(wait, 0))
    except KeyboardInterrupt:
        print("\r", end="")
        if answers:
            if len(answers) == 1:
                return 0
            else:
                a = get_choice("Choose what to say:", answers)
                return a
        else:
            return 0

    return None


def get_choice(message, choices, default=None):
    """
    Give the slave a selection of choices and return the selected index.

    if ``default`` is not None, make that the default choice.
    """
    print(_insert_newlines(message))
    while True:
        for i in range(len(choices)):
            c = "{} - {}".format(i, choices[i])
            if len(c) > 72:
                c = ''.join([c[:69], "..."])
            print(c)
        if default is None:
            ans = input("Enter the number of your choice: ")
        else:
            m = "Enter the number of your choice [{}]: ".format(default)
            ans = input(m)
            if not ans:
                ans = default

        try:
            ans = int(ans)
            if 0 <= ans < len(choices):
                return ans
            else:
                print("Error: value out of range.")
        except ValueError:
            print("Error: invalid entry. Please type an integer.")


def get_bool(message):
    """Ask the slave a "yes" or "no" question and return True or False."""
    print(_insert_newlines(message), "[Y/N]", end=" ")
    while True:
        ans = input().lower()
        if ans in ("y", "1", "yes"):
            return True
        elif ans in ("n", "0", "no"):
            return False
        else:
            m = "Error: invalid entry. Please type \"Y\" (for yes) or \"N\" (for no)."
            print(m, end=" ")


def get_int(message):
    """Ask the slave for a number and return it."""
    print(_insert_newlines(message), end=" ")
    while True:
        ans = input("> ")
        try:
            return int(ans)
        except ValueError:
            print("Error: invalid entry. Please type an integer.", end=" ")


def get_string(message):
    """Ask the slave for a string of text and return it."""
    print(_insert_newlines(message))
    return input("> ")


def beep():
    """Make an audio indication (e.g. beep)."""
    # TODO: Replace with ``print("\a", end="", flush=True)`` when
    # Python 3.2 support is no longer needed
    print("\a", end="")
    sys.stdout.flush()
    
