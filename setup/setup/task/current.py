# coding: utf8

from setup.task import Task
from setup.task.domain import Domain
from setup.task.network import Network
from setup.task.user import User
from setup.config import SYSTEM_TYPE


class Current(Task):
    """Show current configuration info"""
    NAME = "Current Configuration"
    DESCRIPTION = "Current system configuration."

    def main(self):
        """
        Main task function
        """
        self._show_data()

    def _show_data(self):
        """Show configuration data"""
        domain = Domain().get_domain()

        print
        print "[Network]"

        ip, netmask, gateway, name_server = Network().read_defaults()

        print "IP Address: %s" % ip
        print "Network Mask: %s" % netmask
        print "Gateway: %s" % gateway
        print "Name Server: %s" % name_server
        print
        print "[Domain]"
        print "Domain: %s" % domain
        print
        print "[Users]"

        users = User().get_users()

        if users:
            for user in users:
                name = user[1]

                if not name:
                    name = "N/A"

                print "* %s (%s)" % (user[2], name)

        else:
            print "No users yet."

        print
