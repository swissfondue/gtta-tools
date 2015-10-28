# coding: utf8

from subprocess import call
from setup.task import Task
from os import environ


class Login(Task):
    """Login task"""
    NAME = "System Login"
    DESCRIPTION = "System login using virtual console for maintenance purposes."

    def main(self):
        """Main task function"""
        try:
            if environ.get("SSH_TTY"):
                call(["/bin/login"])
            else:
                call(["/sbin/getty", "38400", "tty1"])

        except Exception:
            pass

        print
