# -*- coding: utf-8 -*-

from os import path, geteuid
from sys import exit
from setup.config import SETUP_COMPLETED_FLAG, TASKS_ENABLED, FIRST_TIME_GREETING_TEXT, GREETING_TEXT
from setup.task import Task
from setup.error import SetupError, InvalidTaskError, QuitMenu
from setup import show_menu

def load_task(task):
    """
    Load task
    """
    try:
        module = __import__('setup.task.' + task, globals(), locals(), [ '' ])
        class_name = getattr(module, task.capitalize())

        task = class_name()

        if not isinstance(task, Task):
            raise InvalidTaskError

    except ( ImportError, AttributeError ):
        raise InvalidTaskError

    return task

def first_time():
    """
    First time setup
    """
    print FIRST_TIME_GREETING_TEXT
    print

    number = 1

    for task in TASKS_ENABLED:
        task = load_task(task)

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

def configuration():
    """
    Regular configuration process
    """
    print GREETING_TEXT
    print

    tasks = []
    task_objects = []

    for task in TASKS_ENABLED:
        task = load_task(task)

        if not task.FIRST_TIME_ONLY:
            tasks.append(task.NAME)
            task_objects.append(task)

    while True:
        try:
            choice = show_menu(tasks, allow_quit=True)
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

    try:
        if not path.exists(SETUP_COMPLETED_FLAG):
            first_time()
        else:
            configuration()

    except SetupError as e:
        print str(e)

if __name__ == '__main__':
    main()
