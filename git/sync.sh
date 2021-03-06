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

        -s|--strategy)
            STRATEGY=$2
            shift
            ;;

        -k|--key)
            KEY_FILENAME=$2
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

if [ -z $DIR ] || [ -z $STRATEGY ] || [ -z $EMAIL ];
then
    echo "Invalid arguments."
    exit 1;
fi;

if [ ! -d $DIR/.git ];
then
    echo "Git not inited. Run init.sh."
    exit 1;
fi;

HOMEDIR=$(getent passwd `whoami` | cut -d: -f6)
export HOME=$HOMEDIR

if [ ! -z $KEY_FILENAME ] && [ -e $HOMEDIR/.ssh/$KEY_FILENAME ];
then
    { eval `ssh-agent`; ssh-add $HOMEDIR/.ssh/$KEY_FILENAME; } &>/dev/null;
fi;

if [ $STRATEGY == "theirs" ];
then
    STRATEGY="ours";
else
    STRATEGY="theirs";
fi;

export GIT_SSL_NO_VERIFY=true
GIT_CMD="git --git-dir $DIR/.git --work-tree $DIR"
CHANGED_COUNT=$($GIT_CMD status --porcelain 2>/dev/null | wc -l)
MESSAGE="$(date +'%Y-%m-%d %H:%M'), $EMAIL, $CHANGED_COUNT modified file(s)"

if [ $CHANGED_COUNT == 0 ];
then
    $GIT_CMD fetch --all
    $GIT_CMD merge origin/master
    $GIT_CMD push -u origin master
else
    $GIT_CMD add .
    $GIT_CMD commit -m "$MESSAGE"
    $GIT_CMD fetch --all
    $GIT_CMD branch old-master

    # check if we have origin/master branch available
    ORIGIN_MASTER=`$GIT_CMD branch --all | grep origin/master` || true
    BRANCH_TO_RESET=origin/master

    if [ -z $ORIGIN_MASTER ]
    then
        BRANCH_TO_RESET=master
    fi

    $GIT_CMD reset --hard $BRANCH_TO_RESET
    $GIT_CMD merge old-master -X $STRATEGY -m "Merged using '$STRATEGY' strategy"
    $GIT_CMD branch -D old-master
    $GIT_CMD push -u origin master
fi;
