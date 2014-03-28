# -*- coding: utf-8 -*-

from os import path
from re import match, findall, DOTALL
from shutil import copy2
from subprocess import call, Popen, PIPE
from time import sleep
from setup.task import Task
from setup.error import SystemCommandError
from setup import show_menu, get_input

_IP_REGEXP = '(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])'

_NETWORK_CONFIG_PATH = '/etc/network/interfaces'
_DNS_CONFIG_PATH = '/etc/resolv.conf'
_BACKUP_EXTENSION = 'bak'

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

_DHCP_CONFIG_TEMPLATE = '''
# loopback
auto lo
iface lo inet loopback

# the primary network interface
auto eth0
iface eth0 inet dhcp\n'''

_DNS_CONFIG_TEMPLATE = '''nameserver %(nameserver)s\n'''

class Network(Task):
    """
    Network configuration task
    """
    NAME = 'Network Configuration'
    DESCRIPTION = 'System network configuration: IP address, network mask and gateway.'
    FORBIDDEN_TOOL_PARAMS = ("&&", "<", ">", "|", "*", "`")

    def main(self):
        """
        Main task function
        """
        handlers = {
            0: self._manual,
            1: self._dhcp,
            2: self._network_tools
        }

        choice = show_menu(("Manual Configuration", "DHCP", "Network Tools"), allow_quit=not self.mandatory)
        handlers[choice]()

        print "Done\n"

    def _validate_ip(self, ip):
        """
        IP address validator
        """
        if not ip:
            return False

        if not match('^' + _IP_REGEXP + '$', ip):
            return False

        return True

    def _validate_tool_params(self, params):
        """
        Tool parameters validator
        """
        if not params:
            return True

        for param in self.FORBIDDEN_TOOL_PARAMS:
            if params.find(param) != -1:
                return False

        return True

    def _validate_ns(self, ip):
        """
        NS address validator
        """
        if not match('^' + _IP_REGEXP + '$', ip):
            return False

        return True

    def _read_defaults(self):
        """
        Read default network settings
        """
        ip, netmask, gateway, nameserver = None, None, None, None

        try:
            cfg = open(_NETWORK_CONFIG_PATH, 'r').read()

            ip = (findall('address ([\d\.]+)', cfg) + [ None ])[0]
            netmask = (findall('netmask ([\d\.]+)', cfg) + [ None ])[0]
            gateway = (findall('gateway ([\d\.]+)', cfg) + [ None ])[0]
            nameserver = (findall('dns-nameservers ([\d\.]+)', cfg) + [ None ])[0]

        except Exception:
            pass

        return ip, netmask, gateway, nameserver

    def _manual(self):
        """
        Manual network configuration
        """
        print '\nManual Network Configuration'

        ip, netmask, gateway, nameserver = self._read_defaults()

        ip = get_input('IP Address', self._validate_ip, False, ip)
        netmask = get_input('Network Mask', self._validate_ip, False, netmask)
        gateway = get_input('Gateway', self._validate_ip, False, gateway)
        nameserver = get_input('Name Server', self._validate_ns, True, nameserver)

        if not nameserver:
            nameserver = gateway

        print '\nSaving...'

        try:
            if not path.exists('%s.%s' % ( _NETWORK_CONFIG_PATH , _BACKUP_EXTENSION )):
                copy2(_NETWORK_CONFIG_PATH, '%s.%s' % ( _NETWORK_CONFIG_PATH , _BACKUP_EXTENSION ))

            if not path.exists('%s.%s' % ( _DNS_CONFIG_PATH , _BACKUP_EXTENSION )):
                copy2(_DNS_CONFIG_PATH, '%s.%s' % ( _DNS_CONFIG_PATH , _BACKUP_EXTENSION ))

            # writing files
            cfg = open(_NETWORK_CONFIG_PATH, 'w')
            cfg.write(_STATIC_CONFIG_TEMPLATE % {
                'address'    : ip,
                'netmask'    : netmask,
                'gateway'    : gateway,
                'nameserver' : nameserver
            })
            cfg.close()

            cfg = open(_DNS_CONFIG_PATH, 'w')
            cfg.write(_DNS_CONFIG_TEMPLATE % {
                'nameserver' : nameserver
            })
            cfg.close()

        except Exception as e:
            print 'FAILED (%s)\x07' % str(e)
            return

        print 'Applying...'

        try:
            commands = (
                'ifconfig eth0 %s netmask %s' % ( ip, netmask ),
                'ifconfig eth0 down',
                'ifconfig eth0 up',
                'ip route flush root 0/0',
                'ifconfig eth0 down',
                'ifconfig eth0 up',
                'route add default gw %s' % gateway
            )

            for command in commands:
                ret_code = call([command], shell=True)

                if ret_code != 0:
                    raise SystemCommandError()

                sleep(2)

        except Exception as e:
            print 'FAILED (%s)\x07' % str(e)
            return

        self.changed = True

    def _dhcp(self):
        """
        DHCP network configuration
        """
        self.changed = False

        print '\nDHCP Network Configuration'
        print 'Getting IP address...'
        ip = None

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
            print "Assigned IP: %s" % ip

        except Exception as e:
            print 'FAILED (%s)\x07' % str(e)
            return

        print 'Saving...'

        try:
            if not path.exists('%s.%s' % ( _NETWORK_CONFIG_PATH , _BACKUP_EXTENSION )):
                copy2(_NETWORK_CONFIG_PATH, '%s.%s' % ( _NETWORK_CONFIG_PATH , _BACKUP_EXTENSION ))

            # writing files
            cfg = open(_NETWORK_CONFIG_PATH, 'w')
            cfg.write(_DHCP_CONFIG_TEMPLATE)
            cfg.close()

        except Exception as e:
            print 'FAILED (%s)\x07' % str(e)
            return

        self.changed = True

    def _network_tools(self):
        """
        Network tools
        """
        tools = {
            0: self._ifconfig,
            1: self._route,
            2: self._ip,
            3: self._iptables,
            4: self._ping,
            5: self._traceroute
        }

        while True:
            print "\n[Network Tools]"

            choice = show_menu(("ifconfig", "route", "ip", "iptables", "ping", "traceroute"))
            print
            tools[choice]()

    def _run_tool(self, tool, params):
        """
        Run tool
        """
        if params and len(params) > 100:
            print "Too long line"
            return

        if params:
            for sanitizer in self.FORBIDDEN_TOOL_PARAMS:
                params = params.replace(sanitizer, "")

            params = params.split(" ")

        else:
            params = []

        print
        print "[%s]" % tool[tool.rfind("/") + 1:]

        try:
            process = Popen([tool] + params, stdout=PIPE, stderr=PIPE)
            data = process.communicate()

            print data[0] or data[1]
        except:
            print "Tool running error"

    def _ifconfig(self):
        """
        Ifconfig command
        """
        params = get_input("Parameters for \"ifconfig\"", self._validate_tool_params, True)
        self._run_tool("/sbin/ifconfig", params)

    def _route(self):
        """
        Route command
        """
        params = get_input("Parameters for \"route\"", self._validate_tool_params, True)
        self._run_tool("/sbin/route", params)

    def _ip(self):
        """
        IP command
        """
        params = get_input("Parameters for \"ip\"", self._validate_tool_params, True)

        if params:
            self._run_tool("/sbin/ip", params)

    def _iptables(self):
        """
        IP tables command
        """
        params = get_input("Parameters for \"iptables\"", self._validate_tool_params, True)

        if params:
            self._run_tool("/sbin/iptables", params)

    def _ping(self):
        """
        Ping command
        """
        params = get_input("Parameters for \"ping\"", self._validate_tool_params, True)

        if params:
            self._run_tool("/bin/ping", "-c3 %s" % params)

    def _traceroute(self):
        """
        Traceroute command
        """
        params = get_input("Parameters for \"traceroute\"", self._validate_tool_params, True)

        if params:
            self._run_tool("/usr/sbin/traceroute", params)
