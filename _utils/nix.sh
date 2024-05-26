#!/usr/bin/env bash

if [ -z "${NO_FORMAT}" ]; then
    printf -- "Formatting...\n"
    if [ -z "${FORMAT_MODULES}" ]; then
        FORMAT_MODULES="isort black flake8"
    fi
    if [ -z "${FORMAT_FILES}" ]; then
        if [ -z "${FORMAT_DIR}" ]; then
            FORMAT_DIR="."
        fi
        FORMAT_FILES="$(find ${FORMAT_DIR} -name "*.py" ! -wholename "*/build/*")"
    fi
    for _file in ${FORMAT_FILES}; do
        printf -- "Formatting file: %s\n" ${_file}
        for _mod in ${FORMAT_MODULES}; do
            python -m ${_mod} ${_file}
        done
    done
fi

if [ -z "${NO_TEST}" ]; then
    printf -- "Testing...\n"
    _PYTHONPATH=${PYTHONPATH}
    export PYTHONPATH=
    # @TODO - cfati: End with /* (if no pattern given)
    if [ -z "${TEST_VENV_PATTERN}" ]; then
        # TEST_VENV_PATTERN="${HOME}/Work/Dev/VEnvs/*"
        TEST_VENV_PATTERN="${HOME}/Work/Dev/VEnvs/*test0"
    fi
    if [ -z "${TEST_WHEEL_DIR}" ]; then
        TEST_WHEEL_DIR="/mnt/e/Work/Dev/Repos/GitHub/CristiFati/pycfutils/src/dist"
    fi
    for _venv in $(ls -d ${TEST_VENV_PATTERN}); do
        printf -- "Using environment: %s\n" ${_venv}
         . "${_venv}/bin/activate"
        python -VV
        python -m pip uninstall -y pycfutils
        python -m pip -v install --no-index -f "${TEST_WHEEL_DIR}" pycfutils
        python -m unittest discover -s "${VIRTUAL_ENV}/lib/python$(python -c "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')")/site-packages/pycfutils/tests"
        python -c "import pycfutils.gui as pg, pycfutils.io as pio;print('Press a key: ', pio.read_key(1))"
        python -m pip uninstall -y pycfutils
        deactivate
    done
    export PYTHONPATH=${_PYTHONPATH}
fi
