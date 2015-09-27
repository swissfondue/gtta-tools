# coding: utf8

from hashlib import sha256
from re import match
from setup.task import Task
from setup.error import QuitMenu
from setup import get_input, show_menu
import string
import random

_EMAIL_REGEXP = r"^[^\s@]+@[^@]+\.[^@]+$"
_ADMIN_ROLE = "admin"
_KEYBOARD_HELP = """
If you are using a national keyboard, you may enter special symbols using the following key combinations
(AltGr below means "Alt Graph" key to the right of the space bar):
* German (PC): "@" - AltGr+Q
* German (Mac): "@" - Shift+2, "-" - /
* French (PC): "@" - AltGr+0, "-" - 6, "." - Shift+;
* Spanish (PC): "@" - AltGr+2
* Italian (PC): "@" - AltGr+ò
"""


class User(Task):
    """Add user task"""
    NAME = "Users"
    DESCRIPTION = "Add / Modify accounts in the system."
    DEFAULT_EMAIL = "default@user.com"
    DEFAULT_PASSWORD = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(8))
    db_password = None

    def main_automatic(self):
        """Main automatic task function"""
        kwargs = {
            "email": self.DEFAULT_EMAIL,
            "password": self.DEFAULT_PASSWORD
        }

        self._update_user(**kwargs) if self._user_exists(self.DEFAULT_EMAIL) else self._create_user(**kwargs)

    def main(self):
        """
        Main task function
        """
        handlers = {
            0: self._create_user,
            1: self._update_user
        }

        while True:
            if self.mandatory and self.changed:
                break

            try:
                choice = show_menu((
                        "Add User",
                        "Modify User"
                    )
                )

            except QuitMenu:
                print
                break

            print
            email, password = self._get_input()

            if email and password:
                handlers[choice](email, password)

    def _get_input(self):
        """Get email and password"""
        print _KEYBOARD_HELP
        print "\nUser Details"

        try:
            email = get_input("E-mail", self._validate_email)
            password = get_input("Password", self._validate_password)

        except KeyboardInterrupt:
            return None, None

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

        return email, password

    def _create_user(self, email, password):
        """Create user"""
        self.print_manual_only_text("\nSaving...")

        try:
            if self._user_exists(email):
                raise Exception("User Already Exists")

            password_hash = sha256()
            password_hash.update(password)
            password_hash = password_hash.hexdigest()

            conn = self.connect_db()
            c = conn.cursor()

            c.execute("INSERT INTO users(email, password, role) VALUES(%s, %s, %s)", (
                email,
                password_hash,
                _ADMIN_ROLE
            ))
            conn.commit()

            self.changed = True
            self.print_manual_only_text("Success.")

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))

        self.print_manual_only_text("")

    def _update_user(self, email, password):
        """Update user"""
        self.print_manual_only_text("\nUpdating...")

        try:
            if not self._user_exists(email):
                raise Exception("No User With Such E-mail")

            password_hash = sha256()
            password_hash.update(password)
            password_hash = password_hash.hexdigest()

            conn = self.connect_db()
            c = conn.cursor()
            c.execute("UPDATE users SET password = %s WHERE email = %s", (password_hash, email))
            conn.commit()

            self.changed = True
            self.print_manual_only_text("Success.")

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))

        self.print_manual_only_text("")

    def _validate_email(self, email):
        """User e-mail validator"""
        if not email:
            return False

        if not match(_EMAIL_REGEXP, email):
            return False

        return True

    def _user_exists(self, email):
        """Check if user exists"""
        if not match(_EMAIL_REGEXP, email):
            return False

        conn = self.connect_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email = %s", (email,))

        return c.rowcount

    def _validate_password(self, password):
        """User password validator"""
        if not password:
            return False

        return True

    def get_users(self):
        """Get a list of users"""
        conn = self.connect_db()
        c = conn.cursor()
        c.execute("SELECT id, name, email FROM users ORDER BY email")

        return c.fetchall()
