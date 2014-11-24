# coding: utf-8

from ConfigParser import ConfigParser
from psycopg2 import connect
from setup.error import NotImplementedError

_CONFIG_PATH = "/opt/gtta/config/gtta.ini"
_DATABASE_NAME = "gtta"
_DATABASE_USER = "gtta"
_DATABASE_PASSWORD = "cqxLvzTW96BbiYoPjiyMbiQpG"


class Task(object):
    """Base task class"""
    NAME = "Base Task"
    DESCRIPTION = "Base task that does nothing."
    FIRST_TIME_ONLY = False

    def __init__(self):
        """Constructor"""
        self.changed = False
        self.mandatory = False
        self.is_startup = False

    def run(self, mandatory=False):
        """Run task"""
        self.mandatory = mandatory

        while True:
            self.main()

            if self.mandatory and not self.changed:
                continue

            break

    def main(self):
        """Main task function"""
        raise NotImplementedError("%s.main" % self.__class__.__name__)

    def read_settings(self):
        """Read GTTA settings"""
        config = ConfigParser()
        config.read(_CONFIG_PATH)
        sections = {}

        for section in config.sections():
            for option in config.options(section):
                if section not in sections:
                    sections[section] = {}

                sections[section][option] = config.get(section, option)

        return sections

    def write_settings(self, settings):
        """Write settings"""
        config = ConfigParser()

        for section, options in settings.iteritems():
            config.add_section(section)

            for option, value in options.iteritems():
                config.set(section, option, value)

        with open(_CONFIG_PATH, "wb") as config_file:
            config.write(config_file)

    def connect_db(self):
        """Connect to db"""
        return connect("dbname=%s user=%s password=%s" % (_DATABASE_NAME, _DATABASE_USER, _DATABASE_PASSWORD))
