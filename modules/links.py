#!/usr/bin/env python
#-*- encoding: utf-8 -*-

# Copyright (c) 2011 Louis Roché
#
# Yppy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# Yppy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with Yppy. If not, see <http://www.gnu.org/licenses/>.

import time
import re
import lxml.html
import urllib.request

htmlheader = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" >
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta content="text/html; charset=UTF-8" http-equiv="content-type" />
<title>Yppy | links</title>
</head>

<body>
"""

htmlfooter = """</body>

</html>"""

class Links(object):
    def __init__(self, bot, conf):
        self.conf = conf
        self.bot = bot
        self.count = 0
        self.htmlcount = 50

    def on_message(self, umask, target, msg):
        chan = target.replace('#', '').lower()
        linkhtml = "%s/%s.html" % (self.conf['linkfile'], (self.conf['host'] + '-' + chan))
        linktxt = "%s/%s.txt" % (self.conf['linkfile'], (self.conf['host'] + '-' + chan))
        linkfav = "%s/%s.fav" % (self.conf['linkfile'], (self.conf['host'] + '-' + chan))

        if msg.startswith("!links"):
            self.bot.message(target, ("liens : http://docs.khady.info/%s.html" % (self.conf['host'] + '-' + chan)))
            return
        
        if msg.startswith("!fav"):
            self.fav(msg, linktxt, linkfav, chan, target, umask)
        
        if "http://" in msg and "!nl" not in msg:
            url = 'http://' + msg.split("http://")[1].split(" ")[0]
        elif "https://" in msg and "!nl" not in msg:
            url = 'https://' + msg.split("https://")[1].split(" ")[0]
        else:
            return
        date = time.strftime('%d/%m/%y %H:%M',time.localtime())
        self.gettitle(target, date, umask, url, linkhtml, linktxt, chan)


    def gettitle(self, target, date, umask, url, linkhtml, linktxt, chan):
        try:
            page = urllib.request.urlopen(url)
            rurl = page.geturl()
            t = lxml.html.parse(rurl)
            title = t.find(".//title").text.replace('\n', '')
            title = re.sub(r'\r\n', ' ', title)
            title = re.sub(r'[\t]+', ' ', title)
            title = re.sub(r'[\n]+', ' ', title)
            title = re.sub(r'[\r]+', ' ', title)
            title = re.sub(r'[ ]+', ' ', title)
            self.title(target, date, umask, rurl, linkhtml, linktxt, title, chan)
        except:
            self.notitle(target, date, umask, linkhtml, linktxt, url, chan)

    def notitle(self, target, date, umask, linkhtml, linktxt, url, chan):
        try:
            fd = open(linktxt, 'a')
            fd.write('%s %s : %s\n' % (date, umask.nick, url))
            fd.close()
            self.count += 1
            if self.count == self.htmlcount:
                self.convertTxtToHtml(linkhtml, linktxt)
                self.count = 0
        except IOError:
            print ("Module links: can't open %s/%s.txt" %(self.conf['linkfile'], target[1:].lower()))

    def title(self, target, date, umask, rurl, linkhtml, linktxt, title, chan):
        try:
            fd = open(linktxt, 'a')
            fd.write('%s %s : %s (%s)\n' % (date, umask.nick, rurl, title))
            fd.close()
            self.count += 1
            if self.count == self.htmlcount:
                self.convertTxtToHtml(linkhtml, linktxt)
                self.count = 0        
        except IOError:
            print ("Module links: can't open %s/%s.txt" %(self.conf['linkfile'], target[1:].lower()))

    def convertTxtToHtml(self, linkhtml, linktxt):
        try:
            fdhtml = open(linkhtml, 'w')
        except IOError:
            print("Module links, can't open file %s" % linkhtml)
            return
        try:
            fdtxt = open(linktxt, 'r')
        except IOError:
            print("Module links, can't open file %s" % linktxt)
            return
        fdhtml.write(htmlheader)
        links = fdtxt.readlines()
        count = 0
        try:
            for link in links:
                line = link.split('http')
                fdhtml.write(line[0])
                if len(line) >= 2:
                    alink = line[1].split(' ')[0]
                    fdhtml.write('<a href="http%s">http%s</a> ' % (alink, alink))
                    end = line[1][len(alink) + 1:]
                    fdhtml.write('%s<br />\n' % end)
                else:
                    fdhtml.write('<br />\n')
                count += 1
                if count == 10:
                    count = 0
                    fdhtml.close()
                    try:
                        fdhtml = open(linkhtml, 'a')
                    except IOError:
                        print("Module links, can't open file %s" % linkhtml)
                        return  

        except IOError:
            print("Module links, can't write html link")
            return
        fdhtml.write(htmlfooter)
        fdhtml.close()
        fdtxt.close()

    def fav(self, msg, linktxt, linkfav, chan, target, umask):
        mess = msg.split()
        if len(mess) == 1 or mess[1] == "last" or mess[1] == '':
            try:
                fdtxt = open(linktxt, 'r')
                fdfav = open(linkfav, 'a')
            except IOError:
                print ("Module links: can't open file")
                return
            links = fdtxt.readlines()
            fdfav.write("%s" % links[len(links) - 1])
            fdtxt.close()
            fdfav.close()
        elif mess[1] == "list":
            self.bot.message(target, "Liste : http://docs.khady.info/%s.fav" % chan)

        elif mess[1].startswith("http"):
            date = time.strftime('%d/%m/%y %H:%M',time.localtime())
            try:
                fdfav = open(linkfav, 'a')
            except IOError:
                print ("Module links: can't open file")
                return
            link = mess[1].split()[0]
            fdfav.write('%s %s : %s\n' % (date, umask.nick, link))
            fdfav.close()
        else:
            self.bot.message(target, "Usage: !fav [last|url|list]" )
        return
