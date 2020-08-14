#!/usr/bin/env bash

GIT_URL="github.com/myst3k/cyberpanel"
GIT_BRANCH="custom"

GIT_DIR=$(dirname "$GIT_URL")
GIT_USER=$(basename "$GIT_DIR")
GIT_REPO=$(basename "$GIT_URL")
GIT_OPTS="?flush_cache=True"
GIT_CONTENT_URL="raw.githubusercontent.com/$GIT_USER/$GIT_REPO/$GIT_BRANCH"

wget --no-cache -q -O cyberpanel.sh "$GIT_CONTENT_URL"/cyberpanel.sh"$GIT_OPTS"
chmod 755 cyberpanel.sh

echo "Run Command: GIT_URL=$GIT_URL BRANCH_NAME=$GIT_BRANCH ./cyberpanel.sh"