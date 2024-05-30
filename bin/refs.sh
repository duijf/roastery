#!/usr/bin/env bash
set -efuo pipefail
rye run -- python -m sphinx.ext.intersphinx dist/docs/objects.inv
