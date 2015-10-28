# coding: utf8

from select import select
from sys import stdin, stdout
from config import MENU_KEYS, MENU_QUIT_KEY
from error import EmptyMenuError, QuitMenu, InvalidTaskError
from setup.task import Task


def load_task(task):
    """Load task"""
    try:
        module = __import__("setup.task." + task, globals(), locals(), [""])
        class_name = getattr(module, task.capitalize())

        task = class_name()

        if not isinstance(task, Task):
            raise InvalidTaskError

    except (ImportError, AttributeError):
        raise InvalidTaskError

    return task


def show_menu(options, allow_quit=True):
    """Show a menu"""
    if not len(options):
        raise EmptyMenuError

    if allow_quit:
        print "Please choose one of the following options (or enter 'q' to quit this menu and enter other configruation settings):\n"
    else:
        print "Please choose one of the following options:\n"

    key = 0

    allowed_keys = []

    if allow_quit:
        allowed_keys.append(MENU_QUIT_KEY)

    for option in options:
        allowed_keys.append(MENU_KEYS[key])

        print "\t%s. %s" % (MENU_KEYS[key], option)
        key += 1

    choice_options = "1"

    if len(options) > 1:
        choice_options += "..%s" % MENU_KEYS[len(options) - 1]

    if allow_quit:
        choice_options += ", %s - quit this menu and enter other configruation settings" % MENU_QUIT_KEY

    choice = None

    while True:
        try:
            print "\nYour choice (%s): " % choice_options,
            stdout.flush()

            rlist, _, _ = select([stdin], [], [])

            if rlist:
                choice = stdin.readline()
                choice = choice.strip("\r\n")
            else:
                print "\nTimed out"
                choice = MENU_QUIT_KEY

        except KeyboardInterrupt:
            if allow_quit:
                print "\nPlease use '%s' to quit" % MENU_QUIT_KEY
            else:
                print "\nPlease choose one of the options above"

            continue

        if choice in allowed_keys:
            break

        if not choice:
            print "\nUnknown option"
        else:
            print "\nUnknown option - %s" % choice

    if choice[0] == MENU_QUIT_KEY:
        raise QuitMenu()

    return MENU_KEYS.find(choice)


def yes_no_validator(value):
    """Validates if value is 'y' or 'n'"""
    return value in ("y", "n", "Y", "N")


def get_input(prompt, validator=None, default=None):
    """Get user input"""
    value = None

    if default:
        prompt += " (%s)" % default

    prompt = "* %s: " % prompt

    while True:
        value = raw_input(prompt)

        if not value:
            value = default

        if validator and validator(value):
            break

        print "Invalid value\n"

    return value
