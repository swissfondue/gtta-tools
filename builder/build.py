#!/usr/bin/env python

from os import mkdir, path, chdir, getcwd
from subprocess import check_call, CalledProcessError
from sys import argv, exit

CLEAN_LIST = (
    ".hg*",
    ".idea",
    ".DS_Store",
    "*.swp",
    "*~",
    "*.svn",
    "*-local.php"
)


class CommandFailed(Exception):
    """Command failed exception"""
    pass


def cleanup():
    """Cleanup"""
    clean_list = (
        "packer_cache",
        "files/web.tgz",
        "files/tools.tgz",
        "/tmp/gtta.zip",
        "/tmp/gtta.sig",
        "/tmp/gtta"
    )

    # remove temporary files
    for entry in clean_list:
        try:
            check_call("rm -rf %s" % entry, shell=True)
        except CalledProcessError:
            pass


def build_vm():
    """Build VM"""
    print "VM Builder"
    print "----------"

    try:
        check_call(["packer", "build", "packer/vm.json"])
    except CalledProcessError:
        raise CommandFailed


def build_distr(version, root_password, user_password):
    """Build distr"""
    print "Distributive Builder"
    print "--------------------"
    print "Building version %s" % version

    source_web = "../../web"
    source_tools = "../../tools"
    destination = "/tmp/gtta"
    web_zip = "files/web.tgz"
    tools_zip = "files/tools.tgz"

    mkdir(destination)

    try:
        print "* Copying files"

        check_call("cp -r %s %s" % (source_web, destination), shell=True)

        mkdir("%s/tools" % destination)
        check_call("cp %s/make_config.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp %s/run_script.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/setup %s/tools" % (source_tools, destination), shell=True)

        # remove temporary files
        for entry in CLEAN_LIST:
            check_call("find %s -iname %s | xargs rm -rf" % (destination, entry), shell=True)

        # encode PHP files
        print "* Encoding files"

        check_call([
            "ioncube53",
            "%s/web" % destination,
            "-o",
            "%s/web-encoded" % destination,
            "--copy",
            "migrations/template.php",
            "--copy",
            "config/console.example.php",
            "--copy",
            "config/main.example.php",
            "--without-loader-check"
        ])

        check_call("rm -r %s/web" % destination, shell=True)
        check_call("mv %s/web-encoded %s/web" % (destination, destination), shell=True)

        # compress
        print "* Compressing"

        check_call("tar czf %s %s/web" % (web_zip, destination), shell=True)
        check_call("tar czf %s %s/tools" % (tools_zip, destination), shell=True)

    except CalledProcessError:
        raise CommandFailed

    try:
        check_call([
            "packer",
            "build",
            "-var",
            "version=%s" % version,
            "-var",
            "root_password=%s" % root_password,
            "-var",
            "user_password=%s" % user_password,
            "packer/distr.json"
        ])
    except CalledProcessError:
        raise CommandFailed


def build_all(version, root_password, user_password):
    """Build all"""
    build_vm()
    build_distr(version, root_password, user_password)


def build_update(version, key_password):
    """Build update"""
    print "Update Builder"
    print "--------------"
    print "Building version %s" % version

    source_web = "../../web"
    source_tools = "../../tools"
    destination = "/tmp/gtta"
    zip_path = "/tmp/gtta.zip"
    sig_path = "/tmp/gtta.sig"
    key_path = "../../../security/keys/update-server.priv"
    output = "../../../builds/%s" % version

    mkdir(destination)

    try:
        print "* Copying files"

        check_call("cp -r %s %s" % (source_web, destination), shell=True)
        check_call("cp files/crontab.txt %s" % destination, shell=True)

        # tools
        mkdir("%s/tools" % destination)
        check_call("cp %s/make_config.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp %s/run_script.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/setup %s/tools" % (source_tools, destination), shell=True)

        # install scripts
        mkdir("%s/install" % destination)

        if path.exists("%s/deploy/scripts/%s" % (source_tools, version)):
            check_call("cp %s/deploy/scripts/%s/* %s/install" % (source_tools, version, destination), shell=True)

            with open("%s/install/version" % destination, "wt") as v:
                v.write(version)

        # remove temporary files
        for entry in CLEAN_LIST:
            check_call("find %s -iname %s | xargs rm -rf" % (destination, entry), shell=True)

        # encode PHP files
        print "* Encoding files"

        check_call([
            "ioncube53",
            "%s/web" % destination,
            "-o",
            "%s/web-encoded" % destination,
            "--copy",
            "migrations/template.php",
            "--copy",
            "config/params.template.php",
            "--without-loader-check"
        ])

        check_call("rm -r %s/web" % destination, shell=True)
        check_call("mv %s/web-encoded %s/web" % (destination, destination), shell=True)

        # compress
        print "* Compressing"

        cwd = getcwd()

        try:
            chdir("/tmp")
            check_call("zip -9 -r %s gtta" % zip_path, shell=True)
        finally:
            chdir(cwd)

        check_call(
            "openssl dgst -sha1 -sign %s -passin pass:%s -out %s %s" % (key_path, key_password, sig_path, zip_path),
            shell=True
        )

        check_call("rm -rf %s" % destination, shell=True)

        # move to builds directory
        if path.exists(output):
            check_call("rm -r %s" % output, shell=True)

        mkdir(output)
        check_call("mv %s %s" % (zip_path, output), shell=True)
        check_call("mv %s %s" % (sig_path, output), shell=True)

    except CalledProcessError:
        raise CommandFailed


def show_help(command=None):
    """Show help"""
    help_texts = {
        None: """Usage: build.py <command> <params>

Available commands:
    vm     - build base virtual machine
    distr  - build distributive based on the virtual machine
    all    - build both vm and distributive
    update - build update
    help   - shows this help""",

        "vm": "Usage: build.py vm",
        "distr": "Usage: build.py distr <version> <root password> <user password>",
        "all": "Usage: build.py all <version> <root password> <user password>",
        "update": "Usage: build.py update <version> <key password>",
        "help": "Usage: build.py help <command>",
    }

    if command not in help_texts:
        raise

    print help_texts[command]


def main():
    """Main function"""
    if len(argv) < 2:
        show_help()
        exit(1)

    handlers = {
        "vm": build_vm,
        "distr": build_distr,
        "all": build_all,
        "update": build_update,
        "help": show_help
    }

    command = argv[1]
    args = argv[2:]

    if not command in handlers:
        print "Unknown command - %s" % command
        exit(2)

    cleanup()

    try:
        handlers[command](*args)
    except TypeError:
        print "Invalid number of parameters."
        show_help(command)
        exit(3)
    except CommandFailed:
        print "Command failed :("
    except KeyboardInterrupt:
        print "Command execution interrupted."

    cleanup()

if __name__ == "__main__":
    main()
