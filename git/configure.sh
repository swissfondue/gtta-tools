#!/bin/bash

# Parse args
while [[ $# > 1 ]]
do
key=$1

case $key in
    -d|--dir)
    DIR=$2
    shift;;
    -r|--repo)
    REPO_URL=$2
    shift;;
    -k|--key)
    KEY_PATH=$2
    shift;;
    *)
    ;;
esac
shift
done

# Git command with dirs
GIT_CMD="git --git-dir $DIR/.git --work-tree $DIR"

# Validate
if [ -z $DIR ] || [ -z $REPO_URL ];
then
	echo "Invalid arguments."
	exit 1;
fi;

$GIT_CMD remote set-url origin $REPO_URL

$GIT_CMD config --global user.name `whoami`
$GIT_CMD config --global user.email `whoami`@test.com

if [ ! -z $KEY_PATH ] && [ -e $KEY_PATH ];
then
    HOMEDIR=$(getent passwd `whoami` | cut -d: -f6)
    cp $KEY_PATH $HOMEDIR/.ssh/
    chmod 600 $HOMEDIR/.ssh/$(basename $KEY_PATH)
fi;
