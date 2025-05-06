#!/usr/bin/env bash

_PYCFU_VER="$(date +"%Y.%m.%d")"
_VFILE="pycfutils/version.py"
_BRANCH_NAME="release_${_PYCFU_VER}"

printf -- "Creating branch %s, and updating file %s\n" "${_BRANCH_NAME}" "${_VFILE}"
git checkout -b "${_BRANCH_NAME}"

_VFILE="${_VFILE}" python -c "import os, time;y, m, d = time.gmtime()[:3];f = open(os.environ['_VFILE'], mode='rt');ls = f.readlines();f.close();ls[0] = ls[0].replace('0, 0, 0', f'{y}, {m}, {d}');f = open(os.environ['_VFILE'], mode='wt');f.writelines(ls);f.close()"

git add "${_VFILE}"

git commit -m "build: bump version to ${_PYCFU_VER}"


# Upload:
# python -m twine upload dist/*
