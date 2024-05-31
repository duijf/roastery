#!/usr/bin/env bash
set -eufo pipefail

git branch -D gh-pages || true
rye run sphinx-build --write-all $PROJECT_ROOT/documentation $PROJECT_ROOT/docs
touch $PROJECT_ROOT/docs/.nojekyll
git checkout -b gh-pages
git add -f docs
rm CNAME
git add CNAME
git commit -m "Build docs"
git push -f origin gh-pages
git checkout -
