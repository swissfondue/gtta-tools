# coding: utf-8

from os import path, getpgrp, unlink
from signal import signal, SIGTERM
from subprocess import Popen, PIPE
from sys import stdout, argv, exit
from time import sleep

PIDS_PATH = "/tmp"

PATHS = (
    "/opt/gtta/scripts",
    "/opt/gtta/scripts/system"
)

INTERPRETERS = {
    "py": {
        "name": "python",
        "env": {
            "PYTHONPATH" : "/opt/gtta/scripts/lib:/opt/gtta/scripts/system/lib"
        },
        "params": []
    },

    "pl": {
        "name": "perl",
        "env": {},
        "params": [
            "-I/opt/gtta/scripts/lib",
            "-I/opt/gtta/scripts/system/lib"
        ]
    },
}

_external_pid = None


def get_script_path(script):
    """
    Get script path
    """
    script_path = None

    for p in PATHS:
        if path.exists("%s/%s" % (p, script)):
            script_path = "%s/%s" % (p, script)
            break

    if not script_path:
        raise Exception("Script not found: %s" % script)

    return script_path


def get_entry_point(script_path):
    """
    Get script entry point
    """
    entry_point = "run.py"

    if not path.exists("%s/%s" % (script_path, entry_point)):
        entry_point = "run.pl"

    if not path.exists("%s/%s" % (script_path, entry_point)):
        raise Exception("Entry point not found")

    return entry_point


def get_interpreter(entry_point):
    """
    Get interpreter
    """
    extension = entry_point[entry_point.rindex(".") + 1:]

    if not extension in INTERPRETERS:
        raise Exception("Interpreter not found")

    return INTERPRETERS[extension]


def sigterm_handler(signum, frame):
    """
    TERM signal handler, waiting for child tasks to exit
    """
    global _external_pid

    print "Killed :("
    stdout.flush()

    try:
        unlink(path.join(PIDS_PATH, _external_pid))
    except Exception as e:
        pass

    sleep(5)

    exit()


def save_pid(pid):
    """
    Save sandbox group pid
    """
    global _external_pid
    _external_pid = pid

    with open(path.join(PIDS_PATH, _external_pid), "w") as pid_file:
        pid_file.write(unicode(getpgrp()))


def main():
    """
    Main function
    """
    global _external_pid

    if len(argv) < 2:
        raise Exception("Usage: python run_script.py <script> [args]")

    # pid translation
    for arg in argv[2:]:
        if arg.startswith("--pid="):
            save_pid(arg[6:])
            break

    script = argv[1]
    script_path = get_script_path(script)
    entry_point = get_entry_point(script_path)
    interpreter = get_interpreter(entry_point)

    params = []

    for arg in argv[2:]:
        if arg.startswith("--pid="):
            continue

        params.append(arg)

    signal(SIGTERM, sigterm_handler)

    command = ["/usr/bin/%s" % interpreter["name"]] + interpreter["params"] + [entry_point] + params
    process = Popen(command, stdout=PIPE, stderr=PIPE, cwd=script_path, env=interpreter["env"])

    # output stdout
    while True:
        line = process.stdout.readline()

        if not line and process.poll() is not None:
            break

        print line,
        stdout.flush()

    # output stderr, if any
    for line in process.stderr:
        print line,
        stdout.flush()

    try:
        unlink(path.join(PIDS_PATH, _external_pid))
    except Exception as e:
        pass

    if process.poll() != 0:
        exit(process.returncode)

main()
