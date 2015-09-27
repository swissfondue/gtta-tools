# coding: utf8


class SetupError(Exception):
    """Base class for all setup errors"""
    def __str__(self):
        """
        Get message
        """
        message = '%s: %s' % ( self.__class__.__name__, self.__doc__ )
        old_message = super(SetupError, self).__str__()

        if old_message:
            message += ' (%s)' % old_message

        return message


class InvalidTaskError(SetupError):
    """Task not found"""
    pass


class EmptyMenuError(SetupError):
    """Menu is empty"""
    pass


class QuitMenu(SetupError):
    """Quit from menu"""
    pass


class SystemCommandError(SetupError):
    """Error executing system command"""
    pass
