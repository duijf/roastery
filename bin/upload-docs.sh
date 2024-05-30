#!/usr/bin/env bash
set -eufo pipefail

git branch -D docs
rye run sphinx-build --write-all $PROJECT_ROOT/docs $PROJECT_ROOT/docs-html
touch $PROJECT_ROOT/docs-html/.nojekyll
git checkout -b docs
git add -f docs-html
git commit -m "Build docs"
git push -f origin docs
