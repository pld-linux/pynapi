#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#  Copyright (C) 2009 Arkadiusz Miśkiewicz <arekm@pld-linux.org>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import re
import sys
import mimetypes
import urllib2
import time
import os
import getopt

try:
    from hashlib import md5 as md5
except ImportError:
    from md5 import md5

napipass = 'iBlm8NTigvru0Jr0'

prog = os.path.basename(sys.argv[0])

video_files = [ 'asf', 'avi', 'divx', 'm2ts', 'mkv', 'mp4', 'mpeg', 'mpg', 'ogm', 'rm', 'rmvb', 'wmv' ]
languages = { 'pl': 'PL', 'en': 'ENG' }

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
    print >> sys.stderr, "Usage: %s [OPTIONS]... [FILE|DIR]..." % prog
    print >> sys.stderr, "Find video files and download matching subtitles from napiprojekt server."
    print >> sys.stderr
    print >> sys.stderr, "Supported options:"
    print >> sys.stderr, "     -h, --help            display this help and exit"
    print >> sys.stderr, "     -l, --lang=LANG       subtitles language"
    print >> sys.stderr, "     -n, --nobackup        make no subtitle backup when in update mode"
    print >> sys.stderr, "     -u, --update          fetch new and also update existing subtitles"
    print >> sys.stderr, "     -d, --dest=DIR        destination directory"
    print >> sys.stderr
    print >> sys.stderr, "pynapi $Revision$"
    print >> sys.stderr
    print >> sys.stderr, "Report bugs to <arekm@pld-linux.org>."

def get_desc_links(digest, file=None):
    # improve me
    re_link = re.compile(r'<a.*?href=\'(http://.*?)\'>', re.IGNORECASE)
    d = ""

    try:
        url = "http://www.napiprojekt.pl/index.php3?www=opis.php3&id=%s&film=%s" % (urllib2.quote(digest), urllib2.quote(file))
        f = urllib2.urlopen(url)
        d = f.read()
        f.close()
    except Exception, e:
        return False
    return re_link.findall(d)

def get_cover(digest):
    cover = ""
    try:
        url = "http://www.napiprojekt.pl/okladka_pobierz.php?id=%s&oceny=-1" % (urllib2.quote(digest))
        f = urllib2.urlopen(url)
        cover = f.read()
        f.close()
        content_type = f.info()['Content-Type']
        extension = mimetypes.guess_all_extensions(content_type)[-1]
    except Exception, e:
        return False
    return (cover, extension)

def main(argv=sys.argv):

    try:
        opts, args = getopt.getopt(argv[1:], "d:hl:nu", ["dest", "help", "lang", "nobackup", "update"])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        return 2

    output = None
    verbose = False
    nobackup = False
    update = False
    lang = 'pl'
    dest = None
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("-l", "--lang"):
            if a in languages:
                lang = a
            else:
                print >> sys.stderr, "%s: unsupported language `%s'. Supported languages: %s" % (prog, a, str(languages.keys()))
                return 1
        elif o in ("-n", "--nobackup"):
            nobackup = True
        elif o in ("-u", "--update"):
            update = True
        elif o in ("-d", "--dest"):
            dest = a
        else:
            print >> sys.stderr, "%s: unhandled option" % prog
            return 1

    if not args:
        usage()
        return 2

    print >> sys.stderr, "%s: Subtitles language `%s'. Finding video files..." % (prog, lang)

    files = []
    for arg in args:
        if os.path.isdir(arg):
            for dirpath, dirnames, filenames in os.walk(arg, topdown=False):
                for file in filenames:
                    if file[-4:-3] == '.' and file.lower()[-3:] in video_files:
                        files.append(os.path.join(dirpath, file))
        else:
            files.append(arg)

    files.sort()

    i_total = len(files)
    i = 0

    for file in files:
        i += 1

        vfile = file + '.txt'
        basefile = file
        if len(file) > 4:
            basefile = file[:-4]
            vfile = basefile + '.txt'
        if dest:
            vfile = os.path.join(dest, os.path.split(vfile)[1])

        if not update and os.path.exists(vfile):
            continue

        if not nobackup and os.path.exists(vfile):
            vfile_bak = vfile + '-bak'
            try:
                os.rename(vfile, vfile_bak)
            except (IOError, OSError), e:
                print >> sys.stderr, "%s: Skipping due to backup of `%s' as `%s' failure: %s" % (prog, vfile, vfile_bak, e)
                continue
            else:
                print >> sys.stderr, "%s: Old subtitle backed up as `%s'" % (prog, vfile_bak)

        print >> sys.stderr, "%s: %d/%d: Processing subtitle for %s" % (prog, i, i_total, file)

        d = md5()
        try:
            d.update(open(file).read(10485760))
        except (IOError, OSError), e:
            print >> sys.stderr, "%s: %d/%d: Hashing video file failed: %s" % (prog, i, i_total, e)
            continue

        url = "http://napiprojekt.pl/unit_napisy/dl.php?l=%s&f=%s&t=%s&v=dreambox&kolejka=false&nick=&pass=&napios=%s" % \
            (languages[lang], d.hexdigest(), f(d.hexdigest()), os.name)

        repeat = 3
        sub = None
        http_code = 200
        while repeat > 0:
            repeat = repeat - 1
            try:
                sub = urllib2.urlopen(url)
                if hasattr(sub, 'getcode'):
                    http_code = sub.getcode() 
                sub = sub.read()
            except (IOError, OSError), e:
                print >> sys.stderr, "%s: %d/%d: Fetching subtitle failed: %s" % (prog, i, i_total, e)
                time.sleep(0.5)
                continue
    
            if http_code != 200:
                print >> sys.stderr, "%s: %d/%d: Fetching subtitle failed, HTTP code: %s" % (prog, i, i_total, str(http_code))
                time.sleep(0.5)
                continue
    
            if sub.startswith('NPc'):
                print >> sys.stderr, "%s: %d/%d: Subtitle NOT FOUND" % (prog, i, i_total)
                repeat = -1
                continue

            repeat = 0

        if sub is None or sub == "":
            print >> sys.stderr, "%s: %d/%d: Subtitle download FAILED" % (prog, i, i_total)
            continue

        if repeat == -1:
            continue

        fp = open(vfile, 'w')
        fp.write(sub)
        fp.close()

        desc = get_desc_links(d.hexdigest(), file)
        if desc:
            print >> sys.stderr, "%s: %d/%d: Description: " % (prog, i, i_total)
            for desc_i in desc:
                print >> sys.stderr, "\t\t%s" % desc_i

        cover_stored = ""
        cover_data = get_cover(d.hexdigest())
        if cover_data:
            cover, extension = cover_data
            fp = open(basefile + extension, 'w')
            fp.write(cover)
            fp.close()
            cover_stored = ", %s COVER STORED (%d bytes)" % (extension, len(cover))

        print >> sys.stderr, "%s: %d/%d: SUBTITLE STORED (%d bytes)%s" % (prog, i, i_total, len(sub), cover_stored)

    return 0

if __name__ == "__main__":
    ret = None
    try:
        ret = main()
    except (KeyboardInterrupt, SystemExit):
        print >> sys.stderr, "%s: Interrupted, aborting." % prog
    sys.exit(ret)
