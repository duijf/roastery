#!/usr/bin/env bash
rm -rf $PROJECT_ROOT/build/docs
rye run sphinx-autobuild --write-all $PROJECT_ROOT/documentation $PROJECT_ROOT/build/docs
