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
import time
import datetime
import random
import json

import pymasterlib as lib
from pymasterlib.constants import *


def show_rules():
    for d in lib.ext_dirs[::-1] + [lib.data_dir]:
        fname = os.path.join(d, "rules.json")
        try:
            with open(fname, 'r') as f:
                rules_list = json.load(f)
                break
        except OSError:
            continue
    else:
        rules_list = []

    for i in range(len(rules_list)):
        m = "{}. {}".format(i + 1, rules_list[i])
        lib.message.show(lib.parse.python_tag(m))


def intro():
    def load_text(ID): return lib.message.load_text("intro", ID)

    m = load_text("ask_master_sex")
    c = [load_text("master_sex_male"), load_text("master_sex_female")]
    choice = lib.message.get_choice(m, c)
    lib.master.sex = FEMALE if choice == 1 else MALE

    if lib.master.sex == FEMALE:
        fname = "names_female.txt"
    else:
        fname = "names_male.txt"

    for d in lib.ext_dirs[::-1] + [lib.data_dir]:
        try:
            with open(os.path.join(d, fname), 'r') as f:
                names_list = f.read().splitlines()
                break
        except OSError:
            continue
    else:
        names_list = []

    name = None
    while not name:
        if names_list:
            name = names_list.pop(random.randrange(len(names_list)))
        else:
            break
    else:
        lib.master.name = name

    m = load_text("ask_slave_sex")
    c = [load_text("slave_sex_male"), load_text("slave_sex_female"),
         load_text("slave_sex_neither")]
    choice = lib.message.get_choice(m, c)
    if choice == 0:
        lib.slave.sex = MALE
    elif choice == 1:
        lib.slave.sex = FEMALE
    else:
        lib.slave.sex = None

    lib.message.show(load_text("hello"))
    m = load_text("ask_slave_name")
    while True:
        lib.slave.name = lib.message.get_string(m)
        if lib.slave.name:
            break

    m = load_text("ask_slave_birthday_month")
    month = lib.message.get_int(m)
    while month < 1 or month > 12:
        month = lib.message.get_int(load_text("invalid_month"))

    valid_days = {2: 29, 4: 30, 6: 30, 9: 30, 11: 30}.get(month, 31)

    day = lib.message.get_int(load_text("ask_slave_birthday_day"))
    while day < 1 or day > valid_days:
        m = load_text("invalid_day").format(valid_days)
        day = lib.message.get_int(m)

    lib.slave.birthday = (month, day)

    m = load_text("my_property_now")
    lib.message.show(m, lib.message.load_text("phrases", "assent"))
    lib.message.show(load_text("read_rules"),
                     lib.message.load_text("phrases", "assent"))

    show_rules()

    lib.message.show(load_text("oath_sign"),
                     lib.message.load_text("phrases", "assent"))

    for d in lib.ext_dirs[::-1] + [lib.data_dir]:
        fname = os.path.join(d, "oath.txt")
        try:
            with open(fname, 'r') as f:
                oath = f.read()
                break
        except OSError:
            continue
    else:
        raise

    oath = lib.parse.python_tag(oath)
    lib.slave.oath = oath
    lib.message.show(oath, lib.message.load_text("phrases", "finished"))

    lib.message.show(load_text("first_chore"))
    lib.assign.chore()

    # Start with a record claiming to have done the activities, so
    # that they aren't granted immediately.
    for i, activity in lib.activities:
        if not lib.slave.activities.setdefault(i, []):
            lib.slave.add_activity(i)


def morning_routine():
    def load_text(ID): return lib.message.load_text("morning_routine", ID)

    if (lib.slave.queued_chore is not None and
            lib.message.get_bool(load_text("chore_ask_completed"))):
        lib.tell.completed_chore()

    if lib.slave.queued_chore is not None:
        t = lib.slave.queued_chore.get("time")
        for activity in lib.slave.queued_chore.get("activities", []):
            try:
                lib.slave.activities[activity].remove(t)
            except (KeyError, ValueError):
                print("Warning: Didn't find activity \"{}\" at the time of this chore.".format(activity))
        lib.slave.abandoned_chores.append(lib.slave.queued_chore)
        lib.slave.queued_chore = None

    if lib.slave.sick:
        if lib.message.get_bool(load_text("ask_feeling_better")):
            lib.message.show(load_text("better_yes_response"))
            lib.slave.sick = False
        else:
            lib.message.show(load_text("better_no_response"))

    if not lib.slave.sick:
        e_time = random.randint(45, 2 * ONE_MINUTE + 30)
        lib.message.show_timed(load_text("exercise"), e_time)
        lib.message.beep()
        lib.message.show(load_text("exercise_end"))

    if lib.slave.oath:
        oath = lib.slave.oath
    else:
        for d in lib.ext_dirs[::-1] + [lib.data_dir]:
            fname = os.path.join(d, "oath.txt")
            try:
                with open(fname, 'r') as f:
                    oath = f.read()
                    break
            except OSError:
                continue
        else:
            raise

        oath = lib.parse.python_tag(oath)
        lib.slave.oath = oath

    s_oath = ''.join([c if c.isalnum() else '' for c in oath]).lower()

    wrong = 0
    m = load_text("oath")

    while wrong < 3:
        start = time.time()
        recite = lib.message.get_string(m)
        s_recite = ''.join([c if c.isalnum() else '' for c in recite]).lower()
        end = time.time()
        time_passed = end - start

        if s_recite != s_oath:
            wrong += 1
            m = load_text("oath_wrong")
        # Choosing a limit of 120 WPM, or 10 characters per second.
        elif len(oath) / time_passed > 10:
            m = load_text("oath_cheater")
        else:
            lib.message.show(load_text("oath_success"))
            break
    else:
        lib.message.show(m)
        m = load_text("oath_fail")
        lib.message.show(m, lib.message.load_text("phrases", "assent"))
        lib.message.show(oath, lib.message.load_text("phrases", "finished"))
        m = load_text("oath_fail_punishment")
        lib.message.show(m, lib.message.load_text("phrases", "assent"))
        lib.assign.punishment("oath_fail")

    if not lib.slave.sick and random.random() < 0.25:
        lib.message.show(load_text("have_chore"))
        lib.assign.chore()

    lib.slave.bedtime = None

    if not lib.slave.sick and STARTUP_DAY[1:] == lib.slave.birthday:
        m = load_text("gift_birthday")
        lib.message.show(m)
        gift()


def evening_routine():
    def load_text(ID): return lib.message.load_text("evening_routine", ID)

    if lib.slave.bedtime is not None:
        m = load_text("back_to_bed")
        lib.message.show(m, lib.message.load_text("phrases", "assent"))
        lib.settings.save()
        sys.exit()

    if (lib.slave.queued_chore is not None and
            lib.message.get_bool(load_text("chore_ask_completed"))):
        lib.tell.completed_chore()

    if lib.slave.queued_chore is not None:
        t = lib.slave.queued_chore.get("time")
        for activity in lib.slave.queued_chore.get("activities", []):
            try:
                lib.slave.activities[activity].remove(t)
            except (KeyError, ValueError):
                print("Warning: Didn't find activity \"{}\" at the time of this chore.".format(activity))
        lib.slave.abandoned_chores.append(lib.slave.queued_chore)
        lib.slave.queued_chore = None

    if not lib.message.get_bool(load_text("tasks_ask_completed")):
        m = load_text("tasks_finish")
        lib.message.show(m, lib.message.load_text("phrases", "finished"))

    if (not lib.slave.sick and
            lib.message.get_bool(load_text("ask_night_chore"))):
        lib.assign.night_chore()

    lib.message.show(load_text("goodnight"))

    lib.slave.bedtime = time.time()
    sys.exit()


def rhythm(category, rate_min, rate_max, accel_choices,
           accel_change_time, duration):
    """
    This function was conceived for controlled masturbation, but it
    could theoretically be used for all sorts of things, like spanking
    or exercise.

    ``category`` is a string indicating the category of the rhythm, used
    to find the proper text in text_rhythm.json.  ``rate_min`` and
    ``rate_max`` are the maximum and minimum rates of the rhythm in
    beats per second.  ``accel_choices`` is an iterable of the possible
    acceleration amounts to choose from, in beats per second per second.
    ``accel_change_time`` is the amount of time in between acceleration
    changes in seconds.  ``duration_min`` and ``duration_max`` are the
    minimum and maximum, respectively, possible durations of the rhythm
    in seconds; the actual duration is chosen randomly between these
    two.
    """
    def load_text(ID): return lib.message.load_text("rhythm", ID)

    lib.message.show(load_text("{}_intro".format(category)))

    m = load_text("{}_setup".format(category))
    lib.message.show(m, lib.message.load_text("phrases", "finished"))

    rate = rate_min
    accel = 0
    start_time = time.time()
    segment_start_time = start_time
    loop_start_time = start_time

    while time.time() - start_time < duration:
        if time.time() - segment_start_time >= accel_change_time:
            accel = random.choice(accel_choices)
            segment_start_time += accel_change_time

        lib.message.beep()
        delay = 1 / rate
        time.sleep(delay)

        loop_time = time.time() - loop_start_time
        loop_start_time += loop_time
        rate += loop_time * accel
        rate = max(rate_min, min(rate, rate_max))

    lib.message.show(load_text("{}_end".format(category)))


def rhythm_vaginal_sex(category="sex_vaginal", duration=None):
    if duration is None:
        duration = random.uniform(5 * ONE_MINUTE, 30 * ONE_MINUTE)
    rhythm(category, 0.5, 2.5, (-0.05, 0, 0.05), 10, duration)


def rhythm_anal_sex(category="sex_anal", duration=None):
    if duration is None:
        duration = random.uniform(5 * ONE_MINUTE, 30 * ONE_MINUTE)
    rhythm(category, 1 / 3, 1.5, (-0.025, 0, 0.025), 10, duration)


def masturbate():
    def load_text(ID): return lib.message.load_text("masturbate", ID)
    asked_orgasm = False
    orgasmed = False
    orgasm_denied = time.time() + random.randint(ORGASM_ASK_DELAY_MIN,
                                                 ORGASM_ASK_DELAY_MAX)
    message = load_text("masturbate_start")
    answers = ["", "", ""]
    stop_time = time.time() + lib.request.get_time_limit("masturbation")
    while True:
        if asked_orgasm:
            answers[0] = load_text("ask_orgasm_now")
        elif orgasmed:
            answers[0] = load_text("ask_orgasm_again")
        else:
            answers[0] = load_text("ask_orgasm")
        answers[1] = load_text("ask_stop")
        answers[2] = load_text("naughty_orgasm")
        i = lib.message.get_interruption(message, stop_time - time.time(),
                                         answers)
        message = load_text("masturbate_continue")

        if i == 0:
            asked_orgasm = True

            if time.time() > orgasm_denied:
                if random.randrange(100) < ORGASM_CHANCE:
                    orgasmed = True
                    asked_orgasm = False
                    if random.randrange(100) < ORGASM_WAIT_CHANCE:
                        m = load_text("orgasm_later")
                        a = [load_text("naughty_orgasm")]
                        wait = ORGASM_WAIT
                        deviate = random.uniform(-1, 1)
                        if deviate > 1:
                            wait += (ORGASM_WAIT_MAX - ORGASM_WAIT) * deviate
                        elif deviate < 1:
                            wait += (ORGASM_WAIT - ORGASM_WAIT_MIN) * deviate

                        if lib.message.get_interruption(m, wait, a) is None:
                            lib.message.beep()
                            m = load_text("orgasm_signal")

                            limit = ORGASM_TIME_LIMIT
                            time_deviate = random.uniform(-1, 1)
                            if time_deviate > 1:
                                limit += ((ORGASM_TIME_LIMIT_MAX - limit) *
                                          time_deviate)
                            elif time_deviate < 1:
                                limit += ((limit - ORGASM_TIME_LIMIT_MIN) *
                                          time_deviate)

                            a = [lib.message.load_text("phrases", "finished")]
                            if lib.message.get_interruption(m, limit, a) is None:
                                lib.message.beep()
                                message = load_text("orgasm_too_long")
                        else:
                            lib.tell.had_orgasm()
                            m = load_text("masturbate_stop_order")
                            r = lib.message.load_text("phrases", "assent")
                            lib.message.show(m, r)
                            break
                    else:
                        m = load_text("orgasm_now")

                        limit = ORGASM_TIME_LIMIT
                        deviate = random.uniform(-1, 1)
                        if deviate > 1:
                            limit += ((ORGASM_TIME_LIMIT_MAX -
                                       ORGASM_TIME_LIMIT) * deviate)
                        elif deviate < 1:
                            limit += ((ORGASM_TIME_LIMIT -
                                       ORGASM_TIME_LIMIT_MIN) * deviate)

                        a = [lib.message.load_text("phrases", "finished")]
                        if lib.message.get_interruption(m, limit, a) is None:
                            lib.message.beep()
                            message = load_text("orgasm_too_long")

                else:
                    message = load_text("orgasm_deny")
                    orgasm_denied = time.time() + random.randint(
                        ORGASM_ASK_DELAY_MIN, ORGASM_ASK_DELAY_MAX)
            else:
                message = load_text("orgasm_deny")
            
        elif i == 1:
            m = load_text("masturbate_stop")
            lib.message.show(m, lib.message.load_text("phrases", "thank_you"))
            break
        elif i == 2:
            lib.tell.did_without_permission("masturbation")
            m = load_text("masturbate_stop_order")
            lib.message.show(m, lib.message.load_text("phrases", "assent"))
            break
        else:
            lib.message.beep()
            m = load_text("masturbate_time_up")
            r = lib.message.load_text("phrases", "assent")
            lib.message.show(m, r)
            break


def game_exercise(taunt):
    def load_text(ID): return lib.message.load_text("game", ID)
    lib.message.show(load_text("rules_exercise"))

    score = 0
    score_target = random.randint(5, 10)
    time_start = time.time()
    time_passed = 0

    for _ in range(score_target):
        time_end = time.time()
        time_passed += time_end - time_start
        time_start = time_end
        if time_passed >= AGONY_THRESHOLD:
            time_passed = 0
            lib.message.show_timed(load_text(taunt), 3)

        exercise = random.choice(["burpees", "crunches", "jacks",
                                  "knee_raises", "lunges", "push-ups",
                                  "sit-ups", "squats"])
        n = {"burpees": random.randint(4, 10) * 5,
             "crunches": random.randint(3, 8) * 5,
             "jacks": random.randint(3, 8) * 10,
             "knee_raises": random.randint(4, 10) * 5,
             "lunges": random.randint(1, 3) * 5,
             "push-ups": random.randint(2, 6) * 5,
             "sit-ups": random.randint(3, 8) * 5,
             "squats": random.randint(3, 8) * 5}[exercise]
        m = lib.message.load_text("game_exercise", exercise).format(n)
        lib.message.show(m, lib.message.load_text("phrases", "finished"))


def game_letters(taunt):
    def load_text(ID): return lib.message.load_text("game", ID)
    lib.message.show(load_text("rules_letters"))

    score = 0
    score_target = random.randint(60, 450)
    time_start = time.time()
    time_passed = 0

    while score < score_target:
        time_end = time.time()
        time_passed += time_end - time_start
        time_start = time_end
        if time_passed >= AGONY_THRESHOLD:
            time_passed = 0
            lib.message.show_timed(load_text(taunt), 3)

        c = random.choice([random.randint(48, 57), random.randint(65, 90),
                           random.randint(97, 122)])
        target = chr(c)
        if lib.message.get_string(target) == target:
            lib.message.show_timed(load_text("correct"), 0.7)
            score += 1
        else:
            lib.message.show_timed(load_text("wrong"), 0.7)
            score -= 1


def game_math(taunt):
    def load_text(ID): return lib.message.load_text("game", ID)
    lib.message.show(load_text("rules_math"))

    score = 0
    score_target = random.randint(25, 200)
    time_start = time.time()
    time_passed = 0

    while score < score_target:
        time_end = time.time()
        time_passed += time_end - time_start
        time_start = time_end
        if time_passed >= AGONY_THRESHOLD:
            time_passed = 0
            lib.message.show_timed(load_text(taunt), 3)

        op = random.choice(["+", "-", "*", "/"])
        if op == "+":
            n1 = random.randint(0, 20)
            n2 = random.randint(0, 20)
            if lib.message.get_int("{} + {}".format(n1, n2)) == n1 + n2:
                lib.message.show_timed(load_text("correct"), 0.7)
                score += 1
            else:
                lib.message.show_timed(load_text("wrong"), 0.7)
                score -= 1
        elif op == "-":
            n1 = random.randint(0, 20)
            n2 = random.randint(0, 20)
            if lib.message.get_int("{} - {}".format(n1, n2)) == n1 - n2:
                lib.message.show_timed(load_text("correct"), 0.7)
                score += 1
            else:
                lib.message.show_timed(load_text("wrong"), 0.7)
                score -= 1
        elif op == "*":
            n1 = random.randint(0, 12)
            n2 = random.randint(0, 12)
            if lib.message.get_int("{} * {}".format(n1, n2)) == n1 * n2:
                lib.message.show_timed(load_text("correct"), 0.7)
                score += 1
            else:
                lib.message.show_timed(load_text("wrong"), 0.7)
                score -= 1
        elif op == "/":
            ans = random.randint(0, 12)
            n2 = random.randint(1, 12)
            n1 = ans * n2
            if lib.message.get_int("{} / {}".format(n1, n2)) == ans:
                lib.message.show_timed(load_text("correct"), 0.7)
                score += 1
            else:
                lib.message.show_timed(load_text("wrong"), 0.7)
                score -= 1
        else:
            print("Warning: operator \"{}\" unhandled.".format(op))


def wait_game(taunt):
    games = [game_exercise, game_letters, game_math]
    random.choice(games)(taunt)


def gift_surf():
    def load_text(ID): return lib.message.load_text("masturbate", ID)

    orgasm_time = time.time() + random.randint(20 * ONE_MINUTE, 30 * ONE_MINUTE)
    m = load_text("gift_surf_start")
    a = [load_text("naughty_orgasm")]
    i = lib.message.get_interruption(m, orgasm_time, a)

    if i == 0:
        lib.tell.did_without_permission("masturbation")
        m = load_text("masturbate_stop_order")
        lib.message.show(m, lib.message.load_text("phrases", "assent"))
    else:
        lib.message.beep()
        m = load_text("orgasm_signal")
        limit = lib.request.get_time_limit("__orgasm")
        a = [lib.message.load_text("phrases", "finished")]
        if lib.message.get_interruption(m, limit, a) is None:
            lib.message.beep()
            m = load_text("gift_surf_abort")
            lib.message.show(m, lib.message.load_text("phrases", "assent"))


def gift_other():
    def load_text(ID): return lib.message.load_text("morning_routine", ID)

    m = lib.message.load_text("morning_routine", "gift_special_permission")

    gifts = {}
    for d in [lib.data_dir] + lib.ext_dirs:
        fname = os.path.join(d, "gifts.json")
        try:
            with open(fname, 'r') as f:
                ngifts = json.load(f)
            for i in ngifts:
                gifts[i] = ngifts[i]
        except OSError:
            continue

    while gifts:
        keys = list(gifts.keys())
        i = random.choice(keys)
        requires = gifts[i].setdefault("requires")
        text_choices = gifts[i].setdefault("text", [])

        if text_choices and (not requires or eval(requires)):
            m = lib.parse.python_tag(random.choice(text_choices))
            lib.message.show(m, lib.message.load_text("phrases", "thank_you"))
            break

        del gifts[i]
    else:
        lib.message.show(load_text("gift_none"))


def gift():
    gifts = [gift_surf, gift_other, gift_other, gift_other, gift_other]
    random.choice(gifts)()
