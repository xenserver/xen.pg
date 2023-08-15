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

emit () {
    SHORTSHA=`git log -n1 $1 --abbrev=12 --pretty=format:"%h"`
    SUBJECT=`git log -n1 $1 --pretty=format:"%s"`

    # Obtain date in absolute UTC without a Timezone shift
    DATE=`date -d @$(TZ=UTC git log -n1 --format="%ct" $1) "+%Y-%m-%d %T"`

    git format-patch -kp --no-signature --no-base $1 -N1 --stdout > .git/patches/$BRANCH/backport-$SHORTSHA.patch
    echo "backport-$SHORTSHA.patch #   $DATE - $SUBJECT" >> .git/patches/$BRANCH/snippet-for-series
}

while [[ $# -gt 0 ]]; do
    echo "Considering $1"

    if [[ $1 =~ ^[0-9a-f]{4,40}$ ]]; then
        # Single revision
        emit $1
    else
        # Something more complex.  Ask `git rev-list`
        for R in `git rev-list --reverse $1`; do
            emit $R
        done
    fi

    shift
done
