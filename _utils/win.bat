@echo off

setlocal enabledelayedexpansion enableextensions

if defined NO_TEST (
    goto :eof
)

:_test
    echo Testing...
    set PYTHONPATH=
    :: @TODO - cfati: End with \ (if no pattern given)
    if not defined TEST_VENV_PATTERN (
        :: set TEST_VENV_PATTERN="e:\Work\Dev\VEnvs\"
        set TEST_VENV_PATTERN="e:\Work\Dev\VEnvs\*test0"
    )
    if not defined TEST_WHEEL_DIR (
        set TEST_WHEEL_DIR="e:\Work\Dev\Repos\GitHub\CristiFati\pycfutils\src\dist"
    )
    call bat_funcs dirname %TEST_VENV_PATTERN% _VENVS_DIR
    set _VENVS_DIR=%_VENVS_DIR:"=%
    for /f %%g in ('dir /b %TEST_VENV_PATTERN:"=%') do (
        echo Using environment: "%_VENVS_DIR%\%%g"
        call "%_VENVS_DIR%\%%g\Scripts\activate.bat"
        python -VV
        python -m pip uninstall -y pycfutils
        python -m pip -v install --no-index -f %TEST_WHEEL_DIR% pycfutils
        python -m unittest discover -s "%_VENVS_DIR%\%%g\Lib\site-packages\pycfutils\tests"
        python -c "import sys, pycfutils.gui as pg, pycfutils.io as pio;print('Press a key: ', pio.read_key(1));print(pg.message_box('MBox', sys.version, 320, 200))"
        python -m pip uninstall -y pycfutils
        call deactivate
    )
    goto :eof

