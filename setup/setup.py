# coding: utf-8

from os import path, geteuid
from sys import exit, argv
from setup.config import SETUP_COMPLETED_FLAG, TASKS_ENABLED, FIRST_TIME_GREETING_TEXT, GREETING_TEXT
from setup.task import Task
from setup.error import SetupError, InvalidTaskError, QuitMenu
from setup import show_menu

_STARTUP_FLAG = "start"
_CONFIGURATION_TIMEOUT = 10


def load_task(task, is_startup=False):
    """
    Load task
    """
    try:
        module = __import__('setup.task.' + task, globals(), locals(), [ '' ])
        class_name = getattr(module, task.capitalize())

        task = class_name()

        if not isinstance(task, Task):
            raise InvalidTaskError

        task.is_startup = is_startup

    except ( ImportError, AttributeError ):
        raise InvalidTaskError

    return task

def first_time(is_startup=False):
    """
    First time setup
    """
    print FIRST_TIME_GREETING_TEXT
    print

    number = 1

    for task in TASKS_ENABLED:
        task = load_task(task, is_startup)

        header = '%s (step %i of %i)' % (task.NAME, number, len(TASKS_ENABLED))
        print header
        print '-' * len(header)
        print task.DESCRIPTION

        task.run(mandatory=True)
        number += 1

    try:
        # save setup flag file
        open(SETUP_COMPLETED_FLAG, 'w').close()

    except:
        pass

def configuration(startup=False):
    """
    Regular configuration process
    """
    print GREETING_TEXT
    print

    tasks = []
    task_objects = []

    for task in TASKS_ENABLED:
        task = load_task(task, startup)

        if not task.FIRST_TIME_ONLY:
            tasks.append(task.NAME)
            task_objects.append(task)

    while True:
        timeout = None

        if startup:
            timeout = _CONFIGURATION_TIMEOUT

        try:
            choice = show_menu(tasks, allow_quit=True, timeout=timeout)
        except QuitMenu:
            break

        task = task_objects[choice]

        try:
            print
            print task.NAME
            print '-' * len(task.NAME)
            print task.DESCRIPTION

            task.run(mandatory=False)

        except QuitMenu:
            pass

def main():
    """
    Main function
    """
    if geteuid() != 0:
        exit('Please run this script as root user.')

    is_startup = False

    if len(argv) > 1 and argv[1] == _STARTUP_FLAG:
        is_startup = True

    try:
        if not path.exists(SETUP_COMPLETED_FLAG):
            first_time(is_startup)
        else:
            configuration(is_startup)

    except SetupError as e:
        print str(e)

if __name__ == '__main__':
    main()
