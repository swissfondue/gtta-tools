# coding: utf8

from ConfigParser import ConfigParser
from os import path
from sys import exit, argv

if len(argv) < 3:
    print "Required arguments missing"
    exit(1)

properties_path = argv[1]
configs_path = argv[2]

config_files = (
    configs_path + "/params.template.php",
)

if not path.exists(properties_path):
    print "Properties file does not exist: %s" % properties_path
    exit(1)

config = ConfigParser()
config.read(properties_path)
variables = {}

for section in config.sections():
    for option in config.options(section):
        variables["%s_%s" % (section.upper(), option.upper())] = config.get(section, option)

for config in config_files:
    if not path.exists(config):
        print "Config file does not exist: %s" % config
        exit(1)

    data = open(config).read()

    for (var, value) in variables.iteritems():
        data = data.replace("DEPLOY_%s" % var, value)

    with open(config.replace(".template.php", ".php"), "w") as out:
        out.write(data)
