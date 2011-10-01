#!/usr/bin/python
import re
import collections
import sys 
import simplejson
f = open(sys.argv[1])
pk = 1
j = []
for line in f:

    try:
        a = line.rstrip().split("\t")
        if len(a) is not 3:
            raise IndexError
        d = {}
        d['model'] = 'wordconfuse.Words'
        d['pk'] = str(pk)
        f = {}
        f['word'] = a[0]
        f['definition'] = a[2]
        f['speech'] = a[1]
        d['fields'] = f
        pk = pk + 1
        j.append(d)
    except IndexError:
        sys.stderr.write( "Unable to lookup: " + line + '\n')
        continue
print simplejson.dumps(j)
