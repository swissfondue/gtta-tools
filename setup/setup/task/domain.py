# coding: utf-8

from re import match
from subprocess import call, PIPE
from tempfile import NamedTemporaryFile
from os import unlink
from shutil import copyfile
from setup.task import Task
from setup import get_input, error

_DOMAIN_REGEXP = r"^([a-z\d]+)(\-[a-z\d]+)?(\.[a-z\d]+(\-[a-z\d]+)?){0,}$"
_KEY_FILE = "/opt/gtta/security/ssl/gtta.key"
_CERT_FILE = "/opt/gtta/security/ssl/gtta.crt"


class Domain(Task):
    """
    Domain configuration task
    """
    NAME = "Domain Configuration"
    DESCRIPTION = "System domain setup: set system domain and generate the appropriate self-signed SSL certificate."

    def main(self):
        """
        Main task function
        """
        domain = get_input("Domain", self._validate_domain, False, self._get_domain())

        try:
            self._save_domain(domain)
            self._generate_cert(domain)
            self._restart_apache()

            self.changed = True
            print "Done\n"

        except:
            pass

    def _save_domain(self, domain):
        """
        Save domain settings
        """
        print "\nSaving..."

        try:
            settings = self.read_settings()
            settings["base"]["url"] = "https://%s" % domain
            self.write_settings(settings)

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

    def _generate_cert(self, domain):
        """
        Generate certificate for domain
        """
        print "Generating SSL Certificate..."

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
                            "/OU=Infoguard AG/CN=%s/emailAddress=info@infoguard.ch\"" % (temp_key, temp_csr, domain),
                            "openssl x509 -req -days 3650 -in %s -signkey %s -out %s" % (temp_csr, temp_key, temp_crt),
                        )

                        for command in commands:
                            ret_code = call([command], shell=True, stdout=PIPE, stderr=PIPE)

                            if ret_code != 0:
                                raise error.SystemCommandError()

                        copyfile(temp_crt, _CERT_FILE)
                        copyfile(temp_key, _KEY_FILE)

                    finally:
                        unlink(temp_crt)

                finally:
                    unlink(temp_csr)

            finally:
                unlink(temp_key)

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

    def _restart_apache(self):
        """
        Restart apache
        """
        print "Applying..."

        try:
            ret_code = call(["/etc/init.d/apache2 restart"], shell=True, stdout=PIPE, stderr=PIPE)

            if ret_code != 0:
                raise error.SystemCommandError()

        except Exception as e:
            print "FAILED (%s)\x07" % str(e)
            raise

    def _get_domain(self):
        """
        Get current domain settings
        """
        domain = None

        try:
            settings = self.read_settings()
            domain = settings["base"]["url"]
            domain = domain.replace("https://", "")

            if domain.find(":") != -1:
                domain = domain[:domain.find(":")]

        except:
            pass

        if not domain:
            domain = "gtta.box"

        return domain

    def _validate_domain(self, domain):
        """
        Domain name validator
        """
        if not domain:
            return False

        if not match(_DOMAIN_REGEXP, domain):
            return False

        return True
