# coding: utf-8

from select import select
from sys import stdin, stdout
from setup.config import MENU_KEYS, MENU_QUIT_KEY
from setup.error import EmptyMenuError, QuitMenu


def show_menu(options, allow_quit=True, timeout=None):
    """
    Show a menu
    """
    if not len(options):
        raise EmptyMenuError

    print 'Please choose one of the following options:\n'

    key = 0

    allowed_keys = []

    if allow_quit:
        allowed_keys.append(MENU_QUIT_KEY)

    for option in options:
        allowed_keys.append(MENU_KEYS[key])

        print '\t%s. %s' % ( MENU_KEYS[key], option  )
        key += 1

    choice_options = '1'

    if len(options) > 1:
        choice_options += '..%s' % MENU_KEYS[len(options) - 1]

    if allow_quit:
        choice_options += ', %s - quit' % MENU_QUIT_KEY

    choice = None

    while True:
        try:
            print "\nYour choice (%s): " % choice_options,
            stdout.flush()

            rlist, _, _ = select([stdin], [], [], timeout)

            if rlist:
                choice = stdin.readline()
                choice = choice.strip("\r\n")
            else:
                print "\nTimed out"
                choice = MENU_QUIT_KEY

        except KeyboardInterrupt:
            if allow_quit:
                print '\nPlease use "%s" to quit' % MENU_QUIT_KEY
            else:
                print '\nPlease choose one of the options above'

            continue

        if choice in allowed_keys:
            break

        if not choice:
            print 'Unknown option'
        else:
            print 'Unknown option - %s' % choice

    if choice[0] == MENU_QUIT_KEY:
        raise QuitMenu()

    return MENU_KEYS.find(choice)

def get_input(prompt, validator=None, allow_quit=True, default=None):
    """
    Get user input
    """
    value = None

    if default:
        prompt += ' (%s)' % default

    prompt = '* %s: ' % prompt

    while True:
        try:
            value = raw_input(prompt)

        except KeyboardInterrupt:
            if allow_quit:
                return value
            else:
                print '\nThis value is required\n'
                continue

        if not value:
            value = default

        if validator and validator(value):
            break

        print 'Invalid value\n'

    return value
