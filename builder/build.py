#!/usr/bin/env python

from os import mkdir, path, chdir, getcwd, makedirs
from subprocess import check_call, CalledProcessError
from sys import argv, exit
import build_vars

CLEAN_LIST = (
    ".hg*",
    ".git*",
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


def build_vmware(version):
    """Build VMware"""
    print "GTTA Builder"
    print "--------------------"
    print "Building VMWare version %s" % version

    source_web = build_vars.GTTA_WEB_PATH
    source_tools = build_vars.GTTA_TOOLS_PATH
    output = build_vars.GTTA_OUTPUT
    destination = "/tmp/gtta"
    web_zip = "files/web.tgz"
    tools_zip = "files/tools.tgz"

    mkdir(destination)

    try:
        print "* Copying files"

        check_call("cp -r %s %s/web" % (source_web, destination), shell=True)

        mkdir("%s/tools" % destination)
        check_call("cp %s/make_config.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp %s/run_script.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/setup %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/git %s/tools" % (source_tools, destination), shell=True)

        # remove temporary files
        for entry in CLEAN_LIST:
            check_call("find %s -iname %s | xargs rm -rf" % (destination, entry), shell=True)

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
            "-var", "source_iso=%s" % build_vars.GTTA_ISO,
            "-var", "output_directory=%s" % output,
            "-var", "version=%s" % version,
            "packer/vmware.json"
        ])
    except CalledProcessError:
        raise CommandFailed


def build_update(version, key_password):
    """Build update"""
    print "Update Builder"
    print "--------------"
    print "Building version %s" % version

    source_web = build_vars.GTTA_WEB_PATH
    source_tools = build_vars.GTTA_TOOLS_PATH
    destination = "/tmp/gtta"
    zip_path = "/tmp/gtta.zip"
    sig_path = "/tmp/gtta.sig"
    key_path = build_vars.GTTA_UPDATE_KEY_PATH
    output = "%s/updates/%s" % (build_vars.GTTA_OUTPUT, version)

    mkdir(destination)

    try:
        print "* Copying files"

        check_call("cp -r %s %s/web" % (source_web, destination), shell=True)
        check_call("cp files/crontab.txt %s" % destination, shell=True)

        # tools
        mkdir("%s/tools" % destination)
        check_call("cp %s/make_config.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp %s/run_script.py %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/setup %s/tools" % (source_tools, destination), shell=True)
        check_call("cp -r %s/git %s/tools" % (source_tools, destination), shell=True)

        # install scripts
        mkdir("%s/install" % destination)

        if path.exists("%s/deploy/scripts/%s" % (source_tools, version)):
            check_call("cp %s/deploy/scripts/%s/* %s/install" % (source_tools, version, destination), shell=True)

            with open("%s/install/version" % destination, "wt") as v:
                v.write(version)

        # remove temporary files
        for entry in CLEAN_LIST:
            check_call("find %s -iname %s | xargs rm -rf" % (destination, entry), shell=True)

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

        makedirs(output)
        check_call("mv %s %s" % (zip_path, output), shell=True)
        check_call("mv %s %s" % (sig_path, output), shell=True)

    except CalledProcessError:
        raise CommandFailed


def show_help(command=None):
    """Show help"""
    help_texts = {
        None: """Usage: build.py <command> <params>

Available commands:
    vmware - build distributive based on VMWare virtual machine
    update - build update
    help   - shows this help""",

        "vmware": "Usage: build.py vmware <version>",
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
        "vmware": build_vmware,
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
