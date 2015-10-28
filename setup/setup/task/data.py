# coding: utf8

from subprocess import Popen, PIPE
from setup.task import Task


class Data(Task):
    """Install initial data from Community"""
    NAME = "Install Checks & Scripts"
    DESCRIPTION = "Installing checks & scripts from GTTA Community."

    def main_automatic(self):
        """Main automatic task function"""
        self._install_data()

    def main(self):
        """Main task function"""
        self._install_data()

    def _install_data(self):
        """Show logo"""
        if self.automatic:
            print "\n"

        self.print_manual_only_text("The installation process may take a while, please be patient...")

        try:
            Popen(
                ["/usr/bin/php", "/opt/gtta/current/web/protected/yiic", "initialdata"],
                stdout=PIPE,
                stderr=PIPE
            ).communicate()

            self.print_manual_only_text("Well done!\n")

        except:
            self.print_manual_only_text("Installation has failed.")
            self.print_manual_only_text(
                "Please repeat the installation later or install checks & scripts from GTTA Community manually.\n"
            )

        self.changed = True
