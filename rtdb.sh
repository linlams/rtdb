#!/bin/bash

export HOME=/home/username
export PYTHONPATH=$HOME/lib/pyroscope/pyrocore/src:$HOME/lib/pyroscope/pyrobase/src
RTDBPYPATH=$HOME/bin/rtdb.py

/usr/bin/env python2 $RTDBPYPATH $1
