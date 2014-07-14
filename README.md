rtdb
====

The rtorrent-ps/pyroscope database

config.py - goes in ~/.pyroscope/

rtdb.sh - wrapper that sets some environment variables like PYTHONPATH to let the core script use the pyroscope and pyrocore modules.
  Need to edit HOME and RTDBPYPATH to point to rtdb.py
  
rtdb.py - Python script.  Requires SQLite 3.  

Usage:
rtdb init|collect|update

init - initialize database at ~/.config/rtdb.db
collect - pull latest "uploaded" values from rtorrent
update - push custom key values to rtorrent

New rtorrent fields! - Requires Pyroscope
uploaded_last_day
uploaded_last_week
uploaded_last_month

ex: "rtcontrol uploaded_last_month=-1G --cull --yes --cron"  will cull torrents that haven't uploaded more than a 1GB in the last month.

"rtdb collect" needs to be cron jobbed.  Once an hour is adequate accuracy.  More often is more accurate.  Only changes are captured.
"rtdb update" pushes the custom fields to rtorrent.  Needs to be run before the custom fields are used by rtcontrol.  Can be cron'ed for convenience.
