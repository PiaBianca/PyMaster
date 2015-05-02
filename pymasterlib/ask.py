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

import pymasterlib as lib
from pymasterlib.constants import *


def load_text(ID):
    return lib.message.load_text("ask", ID)


def what():
    m = load_text("ask_what")
    c = [load_text("choice_rules"), load_text("choice_chore"),
         load_text("choice_punishments"), load_text("choice_nothing")]
    choice = lib.message.get_choice(m, c, len(c) - 1)

    if choice == 0:
        lib.scripts.show_rules()
    elif choice == 1:
        chore()
    elif choice == 2:
        punishments()


def chore():
    if lib.slave.queued_chore is not None:
        lib.message.show(lib.slave.queued_chore["text"])
    else:
        lib.message.show(load_text("no_chore"))


def punishments():
    lib.slave.forget()

    punishments_ = []
    for i in lib.slave.misdeeds:
        for misdeed in lib.slave.misdeeds[i]:
            if not misdeed["punished"] and misdeed["punishment"] is not None:
                punishments_.append(misdeed["punishment"])

    if punishments_:
        if len(punishments_) > 1:
            m = load_text("punishments").format(len(punishments_))
            lib.message.show(m)

        for punishment in punishments_:
            lib.message.show(punishment["text"])
    else:
        lib.message.show(load_text("no_punishments"))
