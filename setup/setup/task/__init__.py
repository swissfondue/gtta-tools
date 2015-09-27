# coding: utf8

from ConfigParser import ConfigParser
from psycopg2 import connect

_CONFIG_PATH = "/opt/gtta/config/gtta.ini"
_DATABASE_NAME = "gtta"
_DATABASE_USER = "gtta"


class Task(object):
    """Base task class"""
    NAME = "Base Task"
    SKIP_FOR_SYSTEM_TYPES = ()

    def __init__(self):
        """Constructor"""
        self.changed = False
        self.mandatory = False
        self.automatic = False

    def run(self, mandatory=False, automatic=False):
        """Run task"""
        self.mandatory = mandatory
        self.automatic = automatic

        while True:
            if self.automatic:
                self.main_automatic()
            else:
                self.main()

            if self.mandatory and not self.changed and not self.automatic:
                continue

            break

    def main_automatic(self):
        """Main automatic task function"""
        raise NotImplementedError("%s.main_automatic" % self.__class__.__name__)

    def main(self):
        """Main task function"""
        raise NotImplementedError("%s.main" % self.__class__.__name__)

    def print_manual_only_text(self, text, line_feed=True):
        """Print text only for manual type of configuration"""
        if self.automatic:
            return

        if line_feed:
            print text
        else:
            print text,

    def read_settings(self):
        """Read settings"""
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
        settings = self.read_settings()
        password = settings["database"]["password"]

        return connect("dbname=%s user=%s password=%s" % (_DATABASE_NAME, _DATABASE_USER, password))
