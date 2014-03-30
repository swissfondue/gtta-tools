#!/bin/bash

set -e

# apache config
cat > /etc/apache2/sites-available/gtta-ssl <<\EOT
<VirtualHost *:443>
	ServerAdmin webmaster@localhost

	SSLEngine On
	SSLCertificateFile /opt/gtta/security/ssl/gtta.crt
	SSLCertificateKeyFile /opt/gtta/security/ssl/gtta.key
	SSLCACertificateFile /opt/gtta/security/ca/ca.crt

	DocumentRoot /opt/gtta/current/web

	<Directory />
		Options FollowSymLinks
		AllowOverride All
		SSLVerifyClient optional
		SSLVerifyDepth 10
		SSLOptions +StdEnvVars
		SSLRenegBufferSize 100486000
	</Directory>

	<Directory /opt/gtta/current/web/>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride All
		Order allow,deny
		allow from all
	</Directory>

	ErrorLog ${APACHE_LOG_DIR}/error.log

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
EOT

/etc/init.d/apache2 restart

# set the password back
/usr/sbin/usermod --password `echo "XmhdtxudvzGY8f72ps2d4c4fe" | mkpasswd --password-fd=0` gtta

# set the login shell back
sed -i '1d' /home/gtta/.bashrc
