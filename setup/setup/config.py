# coding: utf8

from os import path

FIRST_TIME_TASKS = (
    "network",
    "domain",
    "user",
    "passwords",
    "data",
    "info",
    "logo"
)


TASKS = (
    "current",
    "auto",
    "network",
    "domain",
    "user",
    "passwords",
    "data",
    "login",
    "reboot",
)

AUTOMATIC_TASKS = (
    "network",
    "domain",
    "user",
    "info",
)

MENU_KEYS = "123456789abcdefghijklmnoprstuvwxyz"
MENU_QUIT_KEY = "q"

SETUP_COMPLETED_FLAG = "/opt/gtta/.setup-completed"

FIRST_TIME_GREETING_TEXT = """
GTTA - First Time Configuration
-------------------------------------------------------------------------------
This script will help you to set up your GTTA virtual machine. All setup steps
are mandatory. You will be able to change these settings later by running the
setup script (gtta-setup) manually.
-------------------------------------------------------------------------------"""

AUTOMATIC_TEXT = """
Do you whish to use the automatic configuration?

If you choose "yes", the software will try to configure the network and will
leave the default values for domain and user settings. Otherwise, you will
have to enter all settings manually."""

GREETING_TEXT = """
GTTA - Configuration
-------------------------------------------------------------------------------
This script will help you to set up your GTTA virtual machine. Please choose a
section below to configure.
-------------------------------------------------------------------------------"""

TYPE_VMWARE = "vmware"
TYPE_AMAZON = "amazon"
TYPE_VIRTUALBOX = "virtualbox"
TYPE_DEDICATED = "dedicated"
TYPE_HOSTED = (TYPE_AMAZON, TYPE_DEDICATED)

_type = TYPE_VMWARE

if path.exists("/opt/gtta/config/type"):
    try:
        _type = open("/opt/gtta/config/type", "rt").read().strip()
    except:
        _type = TYPE_VMWARE

if not _type:
    _type = TYPE_VMWARE

SYSTEM_TYPE = _type
