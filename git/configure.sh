#!/bin/bash

set -e

# Parse args
while [[ $# > 1 ]];
do
    key=$1

    case $key in
        -d|--dir)
            DIR=$2
            shift
            ;;

        -r|--repo)
            REPO_URL=$2
            shift
            ;;

        -k|--key)
            KEY_PATH=$2
            shift
            ;;

        -e|--e-mail)
            EMAIL=$2
            shift
            ;;

        *)
            ;;
    esac

    shift
done

# Git command with dirs
GIT_CMD="git --git-dir $DIR/.git --work-tree $DIR"
HOMEDIR=$(getent passwd `whoami` | cut -d: -f6)
export HOME=$HOMEDIR

# Validate
if [ -z $DIR ] || [ -z $REPO_URL ] || [ -z $EMAIL ];
then
	echo "Invalid arguments."
	exit 1;
fi;

echo $REPO_URL > /tmp/git_url.txt

$GIT_CMD remote set-url origin $REPO_URL
$GIT_CMD config --global user.name `whoami`
$GIT_CMD config --global user.email $EMAIL

if [ ! -z $KEY_PATH ] && [ -e $KEY_PATH ];
then
    mkdir -p $HOMEDIR/.ssh
    cp $KEY_PATH $HOMEDIR/.ssh/
    chmod 600 $HOMEDIR/.ssh/$(basename $KEY_PATH)
fi;
