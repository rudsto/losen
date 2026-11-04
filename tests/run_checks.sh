#!/bin/sh
cd $HOME/git/losen || exit 1
PY=$HOME/agent-s/.venv/bin/python
echo '=== prompt'
PYTHONPATH=src $PY tests/check_s3_adapt.py
echo '=== claude'
/bin/zsh -ic "cd $HOME/git/losen && PYTHONPATH=src $PY tests/check_claude.py uten; PYTHONPATH=src $PY tests/check_claude.py med; PYTHONPATH=src $PY tests/check_claude.py tenking" 2>&1 | grep -v 'permission denied'
echo '=== losen-s3 --help'
bin/losen-s3 --help 2>&1 | head -8
echo FERDIG
