#!/bin/bash

# Parse args
while [[ $# > 1 ]]
do
key=$1

case $key in
    -d|--dir)
    DIR=$2
    shift;;
    -s|--strategy)
    STRATEGY=$2
    shift;;
    -k|--key)
    KEY_FILENAME=$2
    shift;;
    *)
    ;;
esac
shift
done

if [ ! -d $DIR/.git ];
then
    echo "Git not inited. Run init.sh."
    exit 1;
fi;

if [ -z $DIR ] || [ -z $STRATEGY ];
then
    echo "Invalid arguments."
    exit 1;
fi;

HOMEDIR=$(getent passwd `whoami` | cut -d: -f6)

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

MESSAGE=$(date +%s | sha256sum | base64 | head -c 32 ; echo)
export GIT_SSL_NO_VERIFY=true
GIT_CMD="git --git-dir $DIR/.git --work-tree $DIR"
CHANGED_COUNT=$($GIT_CMD status --porcelain 2>/dev/null | wc -l)

if [ $CHANGED_COUNT == 0 ];
then
    $GIT_CMD fetch --all
    $GIT_CMD merge origin/master
    $GIT_CMD push -u origin master
else
    $GIT_CMD add .
    $GIT_CMD commit -m $MESSAGE;
    $GIT_CMD fetch --all
    $GIT_CMD branch old-master
    $GIT_CMD reset --hard origin/master

    $GIT_CMD merge old-master -X $STRATEGY
    $GIT_CMD branch -D old-master
    $GIT_CMD push -u origin master
fi;