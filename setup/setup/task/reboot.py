# coding: utf8

from subprocess import call
from setup.task import Task


class Reboot(Task):
    """Reboot task"""
    NAME = "System Reboot"
    DESCRIPTION = "Reboots the system."

    def main(self):
        """Main task function"""
        try:
            call(["/sbin/reboot"])
        except Exception:
            pass

        print
