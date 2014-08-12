#!/usr/bin/env python2
import os
import sys
import subprocess
import sqlite3

def createDB():
	try:
		os.makedirs(os.path.expanduser('~/.config'))
	except OSError as e:
		print e

	conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
	c = conn.cursor()
	c.execute('''
		CREATE TABLE IF NOT EXISTS hash_uploaded (
		hash TEXT
		,timestamp TEXT
		,uploaded INTEGER
		,PRIMARY KEY (hash,timestamp)
		)
	''')
	c.execute('CREATE INDEX IF NOT EXISTS hash_uploaded_hash_idx on hash_uploaded (hash)')
	c.execute('''
		CREATE TABLE IF NOT EXISTS hash_alias (
		hash TEXT PRIMARY KEY
		,alias TEXT
		,insert_timestamp TEXT
		)
	''')
	c.execute('CREATE INDEX IF NOT EXISTS hash_alias_hash_idx on hash_alias (hash)')
	c.execute('''
CREATE VIEW IF NOT EXISTS v_hash_uploaded_rpt AS
SELECT
c.hash
,(c.uploaded-d.uploaded) as uploaded_last_day
,(c.uploaded-w.uploaded) as uploaded_last_week
,(c.uploaded-m.uploaded) as uploaded_last_month
,c.uploaded as uploaded_all_time

FROM (
SELECT
v.hash,
v.uploaded

FROM hash_uploaded v

JOIN (SELECT hash,max(timestamp) AS timestamp FROM hash_uploaded group by 1) r
ON r.hash = v.hash
AND r.timestamp = v.timestamp

) c

JOIN (
SELECT
v.hash,
v.uploaded

FROM hash_uploaded v

JOIN (SELECT hash, min(timestamp) AS timestamp FROM hash_uploaded WHERE DATE(timestamp) >= DATE('now','-1 days') GROUP BY 1) o
ON v.hash=o.hash
AND v.timestamp = o.timestamp
) d
on c.hash = d.hash

JOIN (
SELECT
v.hash,
v.uploaded

FROM hash_uploaded v

JOIN (SELECT hash, min(timestamp) AS timestamp FROM hash_uploaded WHERE DATE(timestamp) >= DATE('now','-7 days') GROUP BY 1) o
ON v.hash=o.hash
AND v.timestamp = o.timestamp
) w
on c.hash = w.hash

JOIN (
SELECT
v.hash,
v.uploaded

FROM hash_uploaded v

JOIN (SELECT hash, min(timestamp) AS timestamp FROM hash_uploaded WHERE DATE(timestamp) >= DATE('now','-1 month') GROUP BY 1) o
ON v.hash=o.hash
AND v.timestamp = o.timestamp
) m
on c.hash = m.hash
	''')
	conn.commit()
	conn.close()

def collectDB():
	# setup pyrocore
	from pyrocore import connect
	rt = connect()

	# setup sqlite

	conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
	c = conn.cursor()

	changedUploadedRows = 0
	for t in rt.items():
		#print '|'.join([t.hash,t.alias,str(t.uploaded)])
		c.execute('SELECT hash FROM hash_uploaded WHERE hash = ?',[t.hash])
		if c.fetchone() == None:
			c.execute('INSERT OR IGNORE INTO hash_uploaded VALUES (?,CURRENT_TIMESTAMP,?)',[t.hash,str(t.uploaded)])
			changedUploadedRows += c.rowcount
		else:
			c.execute('''
INSERT INTO hash_uploaded
SELECT
hu.hash,
CURRENT_TIMESTAMP,
? AS input_uploaded

FROM hash_uploaded hu

JOIN (SELECT hash, max(timestamp) AS max_timestamp FROM hash_uploaded WHERE hash = ?) huc
ON hu.hash = huc.hash
AND hu.timestamp = huc.max_timestamp
AND hu.uploaded <> ?

WHERE hu.hash = ?
			''',[str(t.uploaded),t.hash,str(t.uploaded),t.hash])
			changedUploadedRows += c.rowcount
		c.execute('INSERT OR IGNORE INTO hash_alias VALUES (?,?,CURRENT_TIMESTAMP)',[t.hash,t.alias])
	conn.commit()
	conn.close()
	return changedUploadedRows

def updateRT():
	# set up pyrocore
	from pyrocore import connect
	rt = connect()
	proxy = rt.open()
	# set up sqlite
	conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
	c = conn.cursor()
	c.execute ('SELECT * from v_hash_uploaded_rpt')
	while True:
		r = c.fetchone()
		if r == None:
			break
		update_values = []
		update_values.append([r[0].encode('ascii','replace'),'uploaded_last_day',str(r[1])])
		update_values.append([r[0].encode('ascii','replace'),'uploaded_last_week',str(r[2])])
		update_values.append([r[0].encode('ascii','replace'),'uploaded_last_month',str(r[3])])
		for u in update_values:
			try:
				result = proxy.d.set_custom(*u)
				if result != 0:
					print 'something happened on '+u
			except Fault as e:
				print e

def printDB():
	conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
	c = conn.cursor()
	c.execute ('''
		SELECT
		ha.hash
		,ha.alias
		,hu.uploaded
		,hu.timestamp
		FROM hash_alias ha
		
		JOIN hash_uploaded hu
		   ON ha.hash = hu.hash
	''')
	results = c.fetchall()
	for r in results:
		print r

def report():
	conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
	c = conn.cursor()
	c.execute ('SELECT * FROM v_hash_uploaded_rpt')
	while True:
		r = c.fetchone()
		if r == None:
			break
		print r

def getHashDaily(inHash):
	try:
		conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
		c = conn.cursor()
		c.execute('SELECT uploaded_last_day FROM v_hash_uploaded_rpt WHERE hash = ?',[inHash])
		return c.fetchone()[0]
	except sqlite3.IntegrityError:
		return 0
	except TypeError:
		return 0
	conn.close()


def getHashWeekly(inHash):
	try:
		conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
		c = conn.cursor()
		c.execute('SELECT uploaded_last_week FROM v_hash_uploaded_rpt WHERE hash = ?',[inHash])
		return c.fetchone()[0]
	except sqlite3.IntegrityError:
		return 0
	except TypeError:
		return 0
	conn.close()

def getHashMonthly(inHash):
	try:
		conn = sqlite3.connect(os.path.expanduser('~/.config/rtdb.db'))
		c = conn.cursor()
		c.execute('SELECT uploaded_last_month FROM v_hash_uploaded_rpt WHERE hash = ?',[inHash])
		return c.fetchone()[0]
	except sqlite3.IntegrityError:
		return 0
	except TypeError:
		return 0
	conn.close()


def main():
	if len(sys.argv) == 1:
		print 'usage: rtdb [init|collect|report|print]'
	elif sys.argv[1].lower() == 'init':
		createDB()
	elif sys.argv[1].lower() == 'collect':
		collectDB()
		print 'Collect done...'
	elif sys.argv[1].lower() == 'report':
		report()
	elif sys.argv[1].lower() == 'print':
		printDB()
	elif sys.argv[1].lower() == 'getdaily':
		print getHashDaily(sys.argv[2])
	elif sys.argv[1].lower() == 'getweekly':
		print getHashWeekly(sys.argv[2])
	elif sys.argv[1].lower() == 'getmonthly':
		print getHashMonthly(sys.argv[2])
	elif sys.argv[1].lower() == 'update':
		updateRT()
		print 'Update done...'
	elif sys.argv[1].lower() == 'test':
		test()
	else:
		print 'usage: rtdb [init|collect|update|report|print]'
if __name__ == "__main__":
	main()
