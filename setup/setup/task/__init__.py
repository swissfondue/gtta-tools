# -*- coding: utf-8 -*-

from setup.error import NotImplementedError

class Task(object):
    """
    Base task class
    """
    NAME = 'Base Task'
    DESCRIPTION = 'Base task that does nothing.'

    def __init__(self):
        """
        Constructor
        """
        self.changed   = False
        self.mandatory = False

    def run(self, mandatory=False):
        """
        Run task
        """
        self.mandatory = mandatory

        while True:
            self.main()

            if not self.mandatory or self.changed:
                break

    def main(self):
        """
        Main task function
        """
        raise NotImplementedError('%s.main' % self.__class__.__name__)
