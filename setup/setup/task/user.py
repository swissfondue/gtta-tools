# coding: utf-8

from hashlib import sha256
from re import match
from setup.task import Task
from setup import get_input

_EMAIL_REGEXP = r"^[^@]+@[^@]+\.[^@]+$"
_ADMIN_ROLE = "admin"


class User(Task):
    """
    Add user task
    """
    NAME = "Add User"
    DESCRIPTION = "Add admin account to the system."
    db_password = None

    def main(self):
        """
        Main task function
        """
        try:
            email, password = self._get_input()
            self._create_user(email, password)
            self.changed = True
            print "Done\n"

        except:
            pass

    def _get_input(self):
        """
        Get email and password
        """
        print "\nUser Details"

        try:
            email = get_input("E-mail", self._validate_email, False)
            password = get_input("Password", self._validate_password, False)

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

        return email, password

    def _create_user(self, email, password):
        """
        Create user
        """
        print "\nSaving..."

        try:
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

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

    def _validate_email(self, email):
        """
        User e-mail validator
        """
        if not email:
            return False

        if not match(_EMAIL_REGEXP, email):
            return False

        conn = self.connect_db()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email = %s", (email,))

        if c.fetchall():
            return False

        return True

    def _validate_password(self, password):
        """
        User password validator
        """
        if not password:
            return False

        return True
