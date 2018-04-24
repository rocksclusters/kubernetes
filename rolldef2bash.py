#!/usr/bin/env python
import sys
import json
jsonfile = sys.argv[1]
xmlfile  = sys.argv[2]
# read the json defs
f = open(jsonfile)
defaults=json.load(f)
defstr=""
for x in defaults:
	defstr += "%s_ROLLDEFAULT=%s\n" % (x['varname'],x['value'])
f.close()

g = open(xmlfile)
for line in g.readlines():
    if "%DEFAULTS%" in line:
	line = line.replace("%DEFAULTS%",defstr)
    sys.stdout.write(line)
g.close()
