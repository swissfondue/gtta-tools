#!/bin/bash

set -e

# Validate dir
if [ -z $1 ];
then
	echo "Invalid dir."
	exit 1;
fi;

if [ -d $1/.git ];
then
    echo "Git already inited in $1"
    exit 0;
fi;

# Git command with dirs
GIT_CMD="git --git-dir $1/.git --work-tree $1"
HOMEDIR=$(getent passwd `whoami` | cut -d: -f6)
export HOME=$HOMEDIR

# Initing
$GIT_CMD init -q

# Configure
$GIT_CMD remote add origin test.com
