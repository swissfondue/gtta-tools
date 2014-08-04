# coding: utf8

from argparse import ArgumentParser
from os import path, walk, getcwd, chdir, devnull
from subprocess import check_call, CalledProcessError, STDOUT
from yaml import load as load_yaml

PACKAGE_FILE = "package.yaml"


def parse(description_path):
    """Parse package"""
    package = load_yaml(file(description_path, "r"))

    if not package:
        raise Exception("Description file parsing error: %s" % description_path)

    package["version"] = str(package["version"])

    return dict((key, package[key]) for key in ("name", "version", "type"))


def process_package(package_path, destination):
    """Process package"""
    description_path = path.join(package_path, PACKAGE_FILE)

    if not path.isfile(description_path):
        raise Exception("Package description file not found: %s/package.yaml" % package_path)

    package = parse(description_path)
    print "[%s] %s %s" % (package["type"], package["name"], package["version"])

    destination_path = path.join(destination, "%s_%s-%s.zip" % (package["type"], package["name"], package["version"]))
    current_dir = getcwd()

    try:
        p, dir_name = path.split(package_path)
        chdir(path.join(package_path, ".."))

        with open(devnull, "w") as dev_null:
            check_call(["/usr/bin/zip", "-r", destination_path, dir_name], stdout=dev_null, stderr=STDOUT)

    except CalledProcessError:
        print "Error compressing package: %s" % package_path
    finally:
        chdir(current_dir)


def process(source, destination, recursive):
    """Process build"""
    source = path.abspath(source)
    destination = path.abspath(destination)
    
    if not path.isdir(source):
        raise Exception("Not a directory: %s" % source)

    if not path.isdir(destination):
        raise Exception("Not a directory: %s" % destination)

    packages = []

    if recursive:
        for root, dir_names, file_names in walk(source):
            for f in file_names:
                if f == PACKAGE_FILE:
                    packages.append(root)
                    break

    elif path.isfile(path.join(source, PACKAGE_FILE)):
        packages.append(source)

    if len(packages) > 0:
        for package in packages:
            process_package(package, destination)
    else:
        raise Exception("No package%s found in %s" % ("s" if recursive else "", source))


def main():
    """Main function"""
    parser = ArgumentParser()
    parser.add_argument("source", help="Package description file search path")
    parser.add_argument("destination", help="Directory to store compressed packages")
    parser.add_argument("-r", "--recursive", help="Search package description files recursively", action="store_true")
    args = parser.parse_args()

    try:
        process(args.source, args.destination, args.recursive)
    except Exception as e:
        print "Error building packages: %s" % unicode(e)
        raise


if __name__ == "__main__":
    main()
