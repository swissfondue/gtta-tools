# coding: utf-8

from re import match
from subprocess import call, PIPE
from tempfile import NamedTemporaryFile
from os import unlink
from shutil import copyfile
from setup.task import Task
from setup import error

_KEY_FILE = "/opt/gtta/security/ca/ca.key"
_CERT_FILE = "/opt/gtta/security/ca/ca.crt"
_SRL_FILE = "/opt/gtta/security/ca/ca.srl"


class Ca(Task):
    """
    Certificate authority generation task
    """
    NAME = "Root User Certificate Generation"
    DESCRIPTION = "Generate a root certificate that will be used to sign user SSL certificates."
    FIRST_TIME_ONLY = True

    def main(self):
        """
        Main task function
        """
        try:
            self._generate_cert()
            self.changed = True

        except:
            pass

    def _generate_cert(self):
        """
        Generate certificate authority
        """
        print "\nGenerating Root Certificate..."

        try:
            temp_key = NamedTemporaryFile(dir="/tmp", delete=False)
            temp_key.close()
            temp_key = temp_key.name

            try:
                temp_csr = NamedTemporaryFile(dir="/tmp", delete=False)
                temp_csr.close()
                temp_csr = temp_csr.name

                try:
                    temp_crt = NamedTemporaryFile(dir="/tmp", delete=False)
                    temp_crt.close()
                    temp_crt = temp_crt.name

                    try:
                        commands = (
                            "openssl genrsa -out %s 2048" % temp_key,
                            "openssl req -new -key %s -out %s -subj \"/C=CH/ST=Zuerich/L=Zuerich/O=Infoguard AG"
                            "/OU=Infoguard AG/CN=GTTA/emailAddress=info@infoguard.ch\"" % (temp_key, temp_csr),
                            "openssl x509 -req -days 3650 -in %s -signkey %s -out %s" % (temp_csr, temp_key, temp_crt),
                        )

                        for command in commands:
                            ret_code = call([command], shell=True, stdout=PIPE, stderr=PIPE)

                            if ret_code != 0:
                                raise error.SystemCommandError()

                        copyfile(temp_crt, _CERT_FILE)
                        copyfile(temp_key, _KEY_FILE)

                        try:
                            unlink(_SRL_FILE)
                        except:
                            pass

                    finally:
                        unlink(temp_crt)

                finally:
                    unlink(temp_csr)

            finally:
                unlink(temp_key)

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise
