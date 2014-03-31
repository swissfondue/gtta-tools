# coding: utf8

from paramiko import Transport, SFTPClient
from sys import argv, exit
import hglib

VM_LOGIN = "root"
VM_IP = "192.168.1.100"
VM_PASSWORD = "RhYq7iPFamVqvAK86LPFk278G"
WEB_PATH = "/Users/anton/Projects/gtta/src/web"
SCRIPTS_PATH = "/Users/anton/Projects/gtta/src/scripts"
TOOLS_PATH = "/Users/anton/Projects/gtta/src/tools"
REMOTE_VERSIONS_PATH = "/opt/gtta/versions"
REMOTE_WEB_PATH = "/opt/gtta/current/web"
REMOTE_SCRIPTS_PATH = "/opt/gtta/current/scripts"
REMOTE_TOOLS_PATH = "/opt/gtta/current/tools"


def sftp_connect():
    """
    Create SFTP connection
    :rtype: SFTPClient
    """
    transport = Transport((VM_IP, 22))
    transport.connect(username=VM_LOGIN, password=VM_PASSWORD)

    return SFTPClient.from_transport(transport)


def collect_files(hg, version):
    """
    Collect changed files
    :type hg: hgclient
    """
    changed_files = hg.status(rev=version)
    copy_files = []
    remove_files = []

    for f in changed_files:
        operation, name = f

        if name == ".hgtags":
            continue

        if operation == "R":
            remove_files.append(name)
        elif operation in ("M", "A"):
            copy_files.append(name)

    print "Collected files: %d (copy: %d, remove: %d)" % \
            (len(copy_files) + len(remove_files), len(copy_files), len(remove_files))

    return copy_files, remove_files


def copy_files(conn, local_path, remote_path, files):
    """
    Copy files
    :type conn: SFTPClient
    """
    if len(files) > 0:
        print "Copying..."

        for f in files:
            print "- %-60s" % f,

            try:
                conn.put("%s/%s" % (local_path, f), "%s/%s" % (remote_path, f))
                print "OK"

            except:
                print "FAIL"
                raise


def remove_files(conn, path, files):
    """
    Copy files
    :type conn: SFTPClient
    """
    if len(files) > 0:
        print "Removing..."

        for f in files:
            print "- %-60s" % f,

            try:
                conn.remove("%s/%s" % (path, f))
                print "OK"

            except:
                print "FAIL"
                raise


def update_dir(local_path, remote_path, version, previous_version):
    """
    Update directory
    """
    hg = hglib.open(local_path)

    try:
        print "Updating to %s" % version
        hg.update(version)

        copy, remove = collect_files(hg, previous_version)
        conn = sftp_connect()
        copy_files(conn, local_path, remote_path, copy)
        remove_files(conn, remote_path, remove)

    finally:
        print "Rolling back to tip"
        hg.update()


def update_web(version, previous_version):
    """
    Update web part
    :param version:
    :param previous_version:
    """
    # extract ioncube-encoded files from the distr
    print "[web]"
    update_dir(WEB_PATH, REMOTE_WEB_PATH, version, previous_version)
    print


def update_scripts(version, previous_version):
    """
    Update scripts
    """
    # extract ioncube-encoded files from the distr
    # copy new files to the VZ
    print "[scripts]"
    update_dir(SCRIPTS_PATH, REMOTE_SCRIPTS_PATH, version, previous_version)
    print


def update_tools(version, previous_version):
    """
    Updating tools
    """
    print "[tools]"
    # extract tools from the distr, execute install.sh


def update_version(version, previous_version):
    """
    Update version number
    """
    print "[version]"
    # update "current" link, update db version


def main():
    """
    Main function
    """
    if len(argv) < 3:
        print "Usage: update_vm new_version previous_version"
        exit(1)

    print "UPDATING VM: %s -> %s" % (argv[2], argv[1])
    print "---"

    update_web(argv[1], argv[2])
    update_scripts(argv[1], argv[2])
    update_tools(argv[1], argv[2])


if __name__ == "__main__":
    main()
