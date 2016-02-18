# coding: utf8

from subprocess import Popen, PIPE
from setup.task import Task
import string
import random


class Passwords(Task):
    """Change root and user passwords"""
    NAME = "Generate root and user passwords"
    DESCRIPTION = "Generating new root and user passwords."

    def main_automatic(self):
        """Main automatic task function"""
        self._generate_passwords()

    def main(self):
        """Main task function"""
        self._generate_passwords()

    def _generate_passwords(self):
        """Generate passwords"""
        if self.automatic:
            print "\n"

        root_password = "".join(random.choice(string.ascii_lowercase + string.digits) for i in range(8))
        user_password = "".join(random.choice(string.ascii_lowercase + string.digits) for i in range(8))

        print "root password: %s" % root_password
        print "gtta user password: %s\n" % user_password

        try:
            Popen("echo \"root:%s\" | chpasswd" % root_password, stdout=PIPE, stderr=PIPE, shell=True).communicate()
            Popen("echo \"gtta:%s\" | chpasswd" % user_password, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        except:
            self.print_manual_only_text("Generating passwords has failed.")
            self.print_manual_only_text("Please generate passwords manually later.\n")

        self.changed = True
