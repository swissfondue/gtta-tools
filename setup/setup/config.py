# -*- coding: utf-8 -*-

TASKS_ENABLED = (
    #"time",
    "network",
    "domain",
    #"database" - auto,
    #"ca" - auto,
    #"user",
)

MENU_KEYS = "123456789abcdefghijklmnoprstuvwxyz"
MENU_QUIT_KEY = "q"

SETUP_COMPLETED_FLAG = "/opt/gtta/tools/setup/.setup-completed"

FIRST_TIME_GREETING_TEXT = """
GTTA - First Time Configuration
-------------------------------------------------------------------------------
This script will help you to set up your GTTA virtual machine. All setup steps
are mandatory. You will be able to change these settings later by running the
setup script (gtta-setup) manually.
-------------------------------------------------------------------------------"""

GREETING_TEXT = """
GTTA - Configuration
-------------------------------------------------------------------------------
This script will help you to set up your GTTA virtual machine. Please choose a
section below to configure.
-------------------------------------------------------------------------------"""
