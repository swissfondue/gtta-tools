# coding: utf8

from setup.config import AUTOMATIC_TASKS, SYSTEM_TYPE
from setup.task import Task
from setup import load_task


class Auto(Task):
    """Run automatic configuration"""
    NAME = "Automatic Configuration"
    DESCRIPTION = "Automatically configures the system."

    def main(self):
        """Main task function"""
        self._auto()

    def _auto(self):
        """Run automatic configuration"""
        tasks = []

        for task in AUTOMATIC_TASKS:
            task = load_task(task)

            if SYSTEM_TYPE in task.SKIP_FOR_SYSTEM_TYPES:
                continue

            tasks.append(task)

        number = 1

        for task in tasks:
            if task.NAME:
                print "%s: " % task.NAME,

            task.run(mandatory=True, automatic=True)

            if task.changed:
                print "OK"
            else:
                print "FAILED"
                print
                print "Automatic configuration has failed."
                print "Please use manual configuration to configure the system."
                print

                break

            number += 1

        self.changed = True
