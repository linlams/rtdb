#!/bin/bash

export HOME=/home/username
export PYTHONPATH=$HOME/lib/pyroscope/pyrocore/src:$HOME/lib/pyroscope/pyrobase/src
case $1 in 
	collect )
		/usr/bin/env python2 $HOME/src/rtdb/rtdb.py collect;;
	update )
		/usr/bin/env python2 $HOME/src/rtdb/rtdb.py update;;
esac
