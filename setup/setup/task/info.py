# coding: utf8

from setup.config import SETUP_COMPLETED_FLAG, SYSTEM_TYPE
from setup.task import Task
from setup.task.domain import Domain
from setup.task.network import Network
from setup.task.user import User


class Info(Task):
    """Show post-configuration info"""
    NAME = "Configuration Information"
    DESCRIPTION = "Your system has been successfully configured."

    def main_automatic(self):
        """Main automatic task function"""
        self._show_data()

    def main(self):
        """
        Main task function
        """
        self._show_data()

    def _show_data(self):
        """Show configuration data"""
        domain = Domain().get_domain()
        ip, _, _, _ = Network().read_defaults()

        if not ip:
            ip = "N/A"

        try:
            # save setup flag file
            open(SETUP_COMPLETED_FLAG, "w").close()
        except:
            pass

        if self.automatic:
            print "\n"

        print "Domain: %s" % domain
        print "IP Address: %s" % ip
        print

        print "You can point your external domain (e.g. example.com) to this system's IP address."
        print "This will enable you to access the web based administration of GTTA"
        print "via an official domain name (e.g. gtta.example.com)."
        print "Please start the manual setup script under 'domain configuration' to create such a domain entry."
        print "As an alternative you can reach the web based administration of GTTA using a internal domain name."
        print "In the automatic setup GTTA will be given the domain 'gtta.local' which can be accessed"
        print "from your computer by changing the corresponding records on your nameserver or by modifying"
        print "the local hosts file on your workstation (C:\WINDOWS\system32\drivers\etc\hosts in Windows,"
        print "/etc/hosts in Mac OS X and Linux).\n"
        print "Enter https://%s or https://%s (in case you created a host or DNS entry)" % (ip, domain)
        print "in your browser to access the system."

        if self.automatic:
            print "Use the following details to login:"
            print "* Login: %s" % User.DEFAULT_EMAIL
            print "* Password: %s" % User.DEFAULT_PASSWORD
        else:
            print "Use e-mail address and password specified above to login."

        print

        try:
            raw_input("Press enter to continue...")
        except KeyboardInterrupt:
            pass

        self.changed = True