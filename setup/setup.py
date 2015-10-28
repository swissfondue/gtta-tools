# coding: utf8

from os import path, geteuid
from sys import exit
from setup.config import SETUP_COMPLETED_FLAG, FIRST_TIME_TASKS, TASKS, FIRST_TIME_GREETING_TEXT, GREETING_TEXT, \
    AUTOMATIC_TEXT, SYSTEM_TYPE
from setup.error import SetupError, QuitMenu
from setup import show_menu, get_input, yes_no_validator, load_task

_STARTUP_FLAG = "start"
_CONFIGURATION_TIMEOUT = 10


def first_time():
    """First time setup"""
    print FIRST_TIME_GREETING_TEXT
    print AUTOMATIC_TEXT
    print

    try:
        automatic = get_input("Use automatic configuration? Y or N", yes_no_validator, default="Y")
    except KeyboardInterrupt:
        automatic = None

    automatic = automatic.upper() == "Y"
    print

    if automatic:
        print "Automatic Configuration..."

    quit_configuration = True
    tasks = []

    for task in FIRST_TIME_TASKS:
        task = load_task(task)

        if SYSTEM_TYPE in task.SKIP_FOR_SYSTEM_TYPES:
            continue

        tasks.append(task)

    while True:
        number = 1

        for task in tasks:
            if task.NAME:
                if automatic:
                    print "%s: " % task.NAME,
                else:
                    header = "%s (step %i of %i)" % (task.NAME, number, len(tasks))
                    print header
                    print "-" * len(header)
                    print task.DESCRIPTION

            task.run(mandatory=True, automatic=automatic)

            if automatic:
                if task.changed:
                    print "OK"
                else:
                    print "FAILED"
                    quit_configuration = False
                    automatic = False

                    print
                    print "Automatic configuration has failed."
                    print "Please use manual configuration to set up the system."
                    print

                    break

            number += 1

        if quit_configuration:
            break


def configuration():
    """Regular configuration process"""
    print GREETING_TEXT
    print

    tasks = []
    task_objects = []

    for task in TASKS:
        task = load_task(task)

        if SYSTEM_TYPE in task.SKIP_FOR_SYSTEM_TYPES:
            continue

        tasks.append(task.NAME)
        task_objects.append(task)

    while True:
        choice = show_menu(tasks, allow_quit=False)
        task = task_objects[choice]

        try:
            print
            print task.NAME
            print "-" * len(task.NAME)
            print task.DESCRIPTION

            task.run(mandatory=False)

        except QuitMenu:
            pass


def main():
    """Main function"""
    if geteuid() != 0:
        exit("Please run this script as root user.")

    try:
        if not path.exists(SETUP_COMPLETED_FLAG):
            first_time()
        else:
            configuration()

    except SetupError as e:
        print str(e)


if __name__ == "__main__":
    main()
