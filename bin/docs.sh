#!/usr/bin/env bash
rm -rf dist/docs
rye run sphinx-autobuild --write-all $PROJECT_ROOT/documentation $PROJECT_ROOT/build/docs
