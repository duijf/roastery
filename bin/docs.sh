#!/usr/bin/env bash
rm -rf dist/docs
rye run sphinx-autobuild --write-all $PROJECT_ROOT/docs $PROJECT_ROOT/build/docs
