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
import datetime
import time
import random

import pymasterlib as lib
from pymasterlib.constants import *

__all__ = ["python", "python_tag"]


def python(text):
    """Alias to eval (used to ensure that the right names are available)."""
    return eval(text)


def python_tag(text):
    """Return ``text`` with <python> tags evaluated."""
    while "<python>" in text and "</python>" in text:
        tag_begin = text.find("<python>")
        code_begin = tag_begin + len("<python>")
        code_end = text.find("</python>")
        tag_end = code_end + len("</python>")
        text = ''.join([text[:tag_begin], str(eval(text[code_begin:code_end])),
                        text[tag_end:]])

    return text
