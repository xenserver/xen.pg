#!/bin/bash -e

#
# Helper script to backport changesets
#
# Patch name: backport-<12 digit SHA>.patch
# Series entry: <patchname> #   <UTC date> - <commit subject>
#

set -o pipefail

TOP=`git rev-parse --show-toplevel`
cd $TOP || { echo >&2 "Failed to chdir to $TOP"; exit 1; }

SYMREF=`git symbolic-ref HEAD`
BRANCH=${SYMREF##*/}

while [[ $# -gt 0 ]]; do
    echo "Considering $1"

    SHORTSHA=`git log -n1 $1 --abbrev=12 --pretty=format:"%h"`
    SUBJECT=`git log -n1 $1 --pretty=format:"%s"`

    # Obtain date in absolute UTC without a Timezone shift
    DATE=`date -d @$(TZ=UTC git log -n1 --format="%ct" $1) "+%Y-%m-%d %T"`

    git format-patch $1 -N1 --stdout > .git/patches/$BRANCH/backport-$SHORTSHA.patch
    echo "backport-$SHORTSHA.patch #   $DATE - $SUBJECT" >> .git/patches/$BRANCH/snippet-for-series

    shift
done
