# coding: utf8

from os import path
from re import match, findall, DOTALL
from shutil import copy2
from subprocess import call, Popen, PIPE
from time import sleep
from urllib import urlopen
from setup.task import Task
from setup.error import SystemCommandError, QuitMenu
from setup import show_menu, get_input

_IP_REGEXP = "(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"

_NETWORK_CONFIG_PATH = "/etc/network/interfaces"
_DNS_CONFIG_PATH = "/etc/resolv.conf"
_BACKUP_EXTENSION = "bak"

_STATIC_CONFIG_TEMPLATE = """# loopback
auto lo
iface lo inet loopback

# the primary network interface
allow-hotplug eth0
iface eth0 inet static
\taddress %(address)s
\tnetmask %(netmask)s
\tgateway %(gateway)s
\tdns-nameservers %(nameserver)s
\tdns-search local\n"""

_DHCP_CONFIG_TEMPLATE = """
# loopback
auto lo
iface lo inet loopback

# the primary network interface
auto eth0
iface eth0 inet dhcp\n"""

_DNS_CONFIG_TEMPLATE = """nameserver %(nameserver)s\n"""


class Network(Task):
    """Network configuration task"""
    NAME = "Network Configuration"
    DESCRIPTION = "System network configuration: IP address, network mask and gateway."
    FORBIDDEN_TOOL_PARAMS = ("&&", "<", ">", "|", "*", "`")
    network_test_passed = False

    def main_automatic(self):
        """Main automatic task function"""
        try:
            self._dhcp()
        except:
            self.changed = False

        if not self.network_test_passed:
            self.changed = False

    def main(self):
        """Main task function"""
        self.network_test_passed = False

        handlers = {
            0: self._manual,
            1: self._dhcp,
            2: self._network_tools
        }

        while True:
            if self.mandatory and self.network_test_passed:
                break

            if self.changed and not self.network_test_passed:
                print "!!! There seems to be a problem with your network settings."
                print "!!! Please change your network configuration or press 'q' to continue the system"
                print "!!! setup process if you are sure that the provided settings are correct."
                print

            try:
                choice = show_menu((
                        "Manual Configuration",
                        "DHCP <-- use this if you don't know what to choose",
                        "Network Tools"
                    ),
                    allow_quit=(not self.mandatory or self.changed)
                )

            except QuitMenu:
                print
                break

            print
            handlers[choice]()

    def _validate_ip(self, ip):
        """IP address validator"""
        if not ip:
            return False

        if not match("^" + _IP_REGEXP + "$", ip):
            return False

        return True

    def _validate_tool_params(self, params):
        """Tool Arguments validator"""
        if not params:
            return True

        for param in self.FORBIDDEN_TOOL_PARAMS:
            if params.find(param) != -1:
                return False

        return True

    def _validate_ns(self, ip):
        """NS address validator"""
        if not match("^" + _IP_REGEXP + "$", ip):
            return False

        return True

    def read_defaults(self):
        """Read default network settings"""
        ip, netmask, gateway, nameserver = None, None, None, None

        try:
            ifconfig = Popen(["ifconfig eth0"], shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            ip = match(r".*inet addr:(\d+\.\d+\.\d+\.\d+).*", ifconfig, DOTALL)

            if ip:
                ip = ip.group(1)

            netmask = match(r".*Mask:(\d+\.\d+\.\d+\.\d+).*", ifconfig, DOTALL)

            if netmask:
                netmask = netmask.group(1)

            route = Popen(["ip route"], shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            gateway = match(r".*default via (\d+\.\d+\.\d+\.\d+).*", route, DOTALL)

            if gateway:
                gateway = gateway.group(1)

            resolv = open(_DNS_CONFIG_PATH, "r").read()
            nameserver = match(r".*nameserver (\d+\.\d+\.\d+\.\d+).*", resolv, DOTALL)

            if nameserver:
                nameserver = nameserver.group(1)

        except Exception:
            pass

        try:
            cfg = open(_NETWORK_CONFIG_PATH, "r").read()

            if not ip:
                ip = (findall("address ([\d\.]+)", cfg) + [None])[0]

            if not netmask:
                netmask = (findall("netmask ([\d\.]+)", cfg) + [None])[0]

            if not gateway:
                gateway = (findall("gateway ([\d\.]+)", cfg) + [None])[0]

            if not nameserver:
                nameserver = (findall("dns-nameservers ([\d\.]+)", cfg) + [None])[0]

        except Exception:
            pass

        return ip, netmask, gateway, nameserver

    def _network_test(self):
        """Test network connection"""
        self.print_manual_only_text("Testing connection...", False)

        try:
            conn = urlopen("http://google.com")
            data = conn.read()

            if len(data) < 100:
                raise Exception()

            self.print_manual_only_text("OK\n")
            self.network_test_passed = True

        except:
            self.print_manual_only_text("FAILED\n")

    def _manual(self):
        """Manual network configuration"""
        print "[Manual Network Configuration]"

        ip, netmask, gateway, nameserver = self.read_defaults()

        try:
            ip = get_input("IP Address", self._validate_ip, default=ip)
            netmask = get_input("Network Mask", self._validate_ip, default=netmask)
            gateway = get_input("Gateway", self._validate_ip, default=gateway)
            nameserver = get_input("Name Server", self._validate_ns, default=nameserver)

        except KeyboardInterrupt:
            return

        if not nameserver:
            nameserver = gateway

        if not ip or not netmask or not gateway or not nameserver:
            return

        print "\nSaving..."

        try:
            if not path.exists("%s.%s" % (_NETWORK_CONFIG_PATH, _BACKUP_EXTENSION)):
                copy2(_NETWORK_CONFIG_PATH, "%s.%s" % (_NETWORK_CONFIG_PATH, _BACKUP_EXTENSION))

            if not path.exists("%s.%s" % (_DNS_CONFIG_PATH, _BACKUP_EXTENSION)):
                copy2(_DNS_CONFIG_PATH, "%s.%s" % (_DNS_CONFIG_PATH, _BACKUP_EXTENSION))

            # writing files
            cfg = open(_NETWORK_CONFIG_PATH, "w")
            cfg.write(_STATIC_CONFIG_TEMPLATE % {
                "address": ip,
                "netmask": netmask,
                "gateway": gateway,
                "nameserver": nameserver
            })
            cfg.close()

            cfg = open(_DNS_CONFIG_PATH, "w")
            cfg.write(_DNS_CONFIG_TEMPLATE % {
                "nameserver": nameserver
            })
            cfg.close()

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            return

        print "Applying..."

        try:
            commands = (
                "ifconfig eth0 %s netmask %s" % (ip, netmask),
                "ifconfig eth0 down",
                "ifconfig eth0 up",
                "ip route flush root 0/0",
                "ifconfig eth0 down",
                "ifconfig eth0 up",
                "route add default gw %s" % gateway
            )

            for command in commands:
                ret_code = call([command], shell=True)

                if ret_code != 0:
                    raise SystemCommandError()

                sleep(2)

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            return

        self._network_test()
        self.changed = True

    def _dhcp(self):
        """DHCP network configuration"""
        self.changed = False

        self.print_manual_only_text("[DHCP Network Configuration]")
        self.print_manual_only_text("Getting IP address...")

        try:
            ret_code = call(["dhclient eth0"], shell=True)

            if ret_code != 0:
                raise SystemCommandError()

            sleep(2)

            ip_data = Popen(["ifconfig eth0"], shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            ip = match(r".*inet addr:(\d+\.\d+\.\d+\.\d+).*", ip_data, DOTALL)

            if not ip:
                raise SystemCommandError()

            ip = ip.group(1)

            self.print_manual_only_text("Assigned IP: %s <-- USE THIS IP TO CONNECT TO GTTA" % ip)

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            return

        self.print_manual_only_text("Saving...")

        try:
            if not path.exists("%s.%s" % (_NETWORK_CONFIG_PATH, _BACKUP_EXTENSION)):
                copy2(_NETWORK_CONFIG_PATH, "%s.%s" % (_NETWORK_CONFIG_PATH, _BACKUP_EXTENSION))

            # writing files
            cfg = open(_NETWORK_CONFIG_PATH, "w")
            cfg.write(_DHCP_CONFIG_TEMPLATE)
            cfg.close()

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            return

        self._network_test()
        self.changed = True

    def _network_tools(self):
        """Network tools"""
        tools = {
            0: self._ifconfig,
            1: self._route,
            2: self._ip,
            3: self._iptables,
            4: self._ping,
            5: self._traceroute
        }

        while True:
            print "[Network Tools]"

            try:
                choice = show_menu(("ifconfig", "route", "ip", "iptables", "ping", "traceroute"))
            except QuitMenu:
                print
                break

            print
            tools[choice]()

    def _run_tool(self, tool, args):
        """Run tool"""
        if args and len(args) > 100:
            print "Too long line"
            return

        if args:
            for sanitizer in self.FORBIDDEN_TOOL_PARAMS:
                args = args.replace(sanitizer, "")

            args = args.split(" ")

        else:
            args = []

        print
        print "[%s]" % tool[tool.rfind("/") + 1:]

        try:
            process = Popen([tool] + args, stdout=PIPE, stderr=PIPE)
            data = process.communicate()

            print data[0] or data[1]
        except:
            print "Tool running error"

    def _ifconfig(self):
        """Ifconfig command"""
        try:
            args = get_input("Arguments for \"ifconfig\"", self._validate_tool_params)
            self._run_tool("/sbin/ifconfig", args)
        except KeyboardInterrupt:
            pass

    def _route(self):
        """Route command"""
        try:
            args = get_input("Arguments for \"route\"", self._validate_tool_params)
            self._run_tool("/sbin/route", args)
        except KeyboardInterrupt:
            pass

    def _ip(self):
        """IP command"""
        try:
            args = get_input("Arguments for \"ip\"", self._validate_tool_params)

            if args:
                self._run_tool("/sbin/ip", args)

        except KeyboardInterrupt:
            pass

    def _iptables(self):
        """IP tables command"""
        try:
            args = get_input("Arguments for \"iptables\"", self._validate_tool_params)

            if args:
                self._run_tool("/sbin/iptables", args)

        except KeyboardInterrupt:
            pass

    def _ping(self):
        """Ping command"""
        try:
            args = get_input("Arguments for \"ping\"", self._validate_tool_params)

            if args:
                self._run_tool("/bin/ping", "-c3 %s" % args)

        except KeyboardInterrupt:
            pass

    def _traceroute(self):
        """Traceroute command"""
        try:
            args = get_input("Arguments for \"traceroute\"", self._validate_tool_params)

            if args:
                self._run_tool("/usr/sbin/traceroute", args)

        except KeyboardInterrupt:
            pass

    def get_public_ip(self):
        """Get public IP"""
        ip = None

        try:
            conn = urlopen("http://checkip.dyndns.com")
            data = conn.read()

            if len(data) < 100:
                raise Exception()

            ip = findall(r"\d+\.\d+\.\d+\.\d+", data)

            if ip:
                ip = ip[0]

        except:
            pass

        return ip
