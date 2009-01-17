#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# reversed napi 0.16.3.1
# by gim,krzynio,dosiu,hash 2oo8.
# more pythonization by arekm
#
# last modified: 6-I-2oo8
#
# 4pc0h f0rc3
#
# do dzialania potrzebny jest p7zip-full (tak sie nazywa paczka w debianie)
#
# POZDRAWIAMY NASZYCH FANOW!

import hashlib
import sys
import urllib
import subprocess
import tempfile
import os
import getopt

napipass = 'iBlm8NTigvru0Jr0'

prog = os.path.basename(sys.argv[0])

def f(z):
	idx = [ 0xe, 0x3,  0x6, 0x8, 0x2 ]
	mul = [   2,   2,    5,   4,   3 ]
	add = [   0, 0xd, 0x10, 0xb, 0x5 ]

	b = []
	for i in xrange(len(idx)):
		a = add[i]
		m = mul[i]
		i = idx[i]

		t = a + int(z[i], 16)
		v = int(z[t:t+2], 16)
		b.append( ("%x" % (v*m))[-1] )

	return ''.join(b)

def usage():
    print >> sys.stderr, "Usage: %s [-s] <file|dir> [<file|dir> ...]" % sys.argv[0]

try:
    opts, args = getopt.getopt(sys.argv[1:], "hs", ["help", "skip"])
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

output = None
verbose = False
skip = False
for o, a in opts:
    if o == "-v":
        verbose = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-s", "--skip"):
        skip = True
    else:
        print >> sys.stderr, "%s: unhandled option" % prog
        sys.exit(1)

print >> sys.stderr, "%s: Finding video files..." % prog

files = []
for arg in args:
    if os.path.isdir(arg):
        for dirpath, dirnames, filenames in os.walk(arg, topdown=False):
            for file in filenames:
                if file.lower().endswith('.avi'):
                    files.append(os.path.join(dirpath, file))
    else:
        files.append(arg)

files.sort()

i_total = len(files)
i = 0

for file in files:
    i += 1

    vfile = file + '.txt'
    if len(file) > 4:
        vfile = file[:-4] + '.txt'

    if skip and os.path.exists(file):
        continue

    print >> sys.stderr, "%s: %d/%d: Processing subtitle for %s" % (prog, i, i_total, file)

    d = hashlib.md5()
    try:
        d.update(open(file).read(10485760))
    except (IOError, OSError), e:
        print >> sys.stderr, "%s: %d/%d: Hashing video file failed: %s" % (prog, i, i_total, e)
        continue

    url = "http://napiprojekt.pl/unit_napisy/dl.php?l=PL&f=" + d.hexdigest() + "&t=" + f(d.hexdigest()) + "&v=other&kolejka=false&nick=&pass=&napios=" + os.name

    sub = None
    try:
        sub = urllib.urlopen(url)
        sub = sub.read()
    except (IOError, OSError), e:
        print >> sys.stderr, "%s: %d/%d: Fetching subtitle failed: %s" % (prog, i, i_total, e)
        continue

    # XXX: is this standard way for napiproject to signalize error?
    if sub == 'NPc0':
        print >> sys.stderr, "%s: %d/%d: Subtitle NOT FOUND" % (prog, i, i_total)
        continue

    fp = tempfile.NamedTemporaryFile('wb', suffix=".7z", delete=False)
    tfp = fp.name
    fp.write(sub)
    fp.close()

    try:
        cmd = ['/usr/bin/7z', 'x', '-y', '-so', '-p' + napipass, tfp]
        sa = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        (so, se) = sa.communicate(sub)
        retcode = sa.returncode
    except OSError, e:
        se = e
        retcode = True

    os.unlink(tfp)

    if retcode:
        print >> sys.stderr, "%s: %d/%d: Subtitle decompression FAILED: %s" % (prog, i, i_total, se)
        continue

    fp = open(vfile, 'w')
    fp.write(so)
    fp.close()
    os.chmod(vfile, 0644)

    print >> sys.stderr, "%s: %d/%d: STORED (%d bytes)" % (prog, i, i_total, len(so))
