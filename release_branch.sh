#!/usr/bin/env bash
if [ -z "${RELEASE_VERSION_STRING}" ]; then
    RELEASE_VERSION_STRING="$(date +"%Y.%m.%d")"
fi

if [ -z "${VERSION_FILE}" ]; then
    VERSION_FILE="pycfutils/version.py"
fi
if [ ! -f "${VERSION_FILE}" ]; then
    printf -- "Version file %s not found. Exiting\n" "${VERSION_FILE}"
    exit 1
fi

if [ -z "${RELEASE_MARKER}" ]; then
    RELEASE_MARKER="release"
fi

_BRANCH_NAME="${RELEASE_MARKER}_${RELEASE_VERSION_STRING}"

printf -- "Creating branch %s, and updating file %s\n" "${_BRANCH_NAME}" "${VERSION_FILE}"
git checkout -b "${_BRANCH_NAME}"

VERSION_FILE="${VERSION_FILE}" python -c "import os, time;y, m, d = time.gmtime()[:3];f = open(os.environ['VERSION_FILE'], mode='rt');ls = f.readlines();f.close();ls[0] = ls[0].replace('0, 0, 0', f'{y}, {m}, {d}');f = open(os.environ['VERSION_FILE'], mode='wt');f.writelines(ls);f.close()"

git add "${VERSION_FILE}"

git commit -m "build: bump version to ${RELEASE_VERSION_STRING}"


# Build:
# python setup.py bdist_wheel  # sdist

# Upload:
# python -m twine upload dist/*
