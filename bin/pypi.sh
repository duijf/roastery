#!/usr/bin/env bash
set -eufo pipefail

rm -rf $PROJECT_ROOT/dist
rye build
rye publish
