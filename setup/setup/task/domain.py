# coding: utf8

from re import match
from subprocess import call, PIPE
from tempfile import NamedTemporaryFile
from os import unlink
from shutil import copyfile
from setup.task import Task
from setup import get_input, error

_DOMAIN_REGEXP = r"^([a-z\d]+)(\-[a-z\d]+)?(\.[a-z\d]+(\-[a-z\d]+)?){0,}$"
_KEY_FILE = "/opt/gtta/security/ssl/server.key"
_CERT_FILE = "/opt/gtta/security/ssl/server.crt"
_GENERATE_CONFIG = "python /opt/gtta/current/tools/make_config.py /opt/gtta/config/gtta.ini /opt/gtta/current/web/protected/config"


class Domain(Task):
    """Domain configuration task"""
    NAME = "Domain Configuration"
    DESCRIPTION = "System domain setup: set system domain and generate the appropriate self-signed SSL certificate."
    DEFAULT_DOMAIN = "gtta.local"

    def _set_domain(self, domain):
        """Set domain"""
        try:
            self._save_domain(domain)
            self._generate_cert(domain)
            self._generate_config()
            self._restart_apache()
            self.changed = True

        except:
            pass

    def main_automatic(self):
        """Main automatic task function"""
        self._set_domain(self.DEFAULT_DOMAIN)

    def main(self):
        """Main task function"""
        try:
            domain = get_input("Domain", self._validate_domain, default=self.get_domain())
            self._set_domain(domain)
        except KeyboardInterrupt:
            pass

    def _save_domain(self, domain):
        """Save domain settings"""
        self.print_manual_only_text("\nSaving...")

        try:
            settings = self.read_settings()
            settings["base"]["domain"] = domain
            self.write_settings(settings)

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            raise

    def _generate_cert(self, domain):
        """Generate certificate for domain"""
        self.print_manual_only_text("Generating SSL Certificate...")

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
                            "openssl req -new -key %s -out %s -subj \"/C=CH/ST=Zurich/L=Zurich/O=Infoguard AG"
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
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            raise

    def _generate_config(self):
        """Generate software config"""
        self.print_manual_only_text("Generating Software Configuration...")

        try:
            ret_code = call([_GENERATE_CONFIG], shell=True, stdout=PIPE, stderr=PIPE)

            if ret_code != 0:
                raise error.SystemCommandError()

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            raise

    def _restart_apache(self):
        """Restart apache"""
        self.print_manual_only_text("Applying...")

        try:
            ret_code = call(["/etc/init.d/apache2 restart"], shell=True, stdout=PIPE, stderr=PIPE)

            if ret_code != 0:
                raise error.SystemCommandError()

            self.print_manual_only_text("")

        except Exception as e:
            self.print_manual_only_text("FAILED (%s)\x07" % str(e))
            raise

    def get_domain(self):
        """Get current domain settings"""
        domain = None

        try:
            settings = self.read_settings()
            domain = settings["base"]["domain"]

        except:
            pass

        if not domain:
            domain = self.DEFAULT_DOMAIN

        return domain

    def _validate_domain(self, domain):
        """Domain name validator"""
        if not domain:
            return False

        if not match(_DOMAIN_REGEXP, domain):
            return False

        return True
