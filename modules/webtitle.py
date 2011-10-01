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

import re
import lxml.html
import urllib.request

class Webtitle(object):
    def __init__(self, bot, conf):
        self.conf = conf
        self.bot = bot

    def on_message(self, umask, target, msg):
        if "http://" in msg:
            url = 'http://' + msg.split("http://")[1].split(" ")[0]
        elif "https://" in msg:
            url = 'https://' + msg.split("https://")[1].split(" ")[0]
        else:
            return
        try:
            page = urllib.request.urlopen(url)
            trueurl = page.geturl()
            t = lxml.html.parse(trueurl)
            title = t.find(".//title").text.replace('\n', '')
            title = re.sub(r'[ ]+', ' ', title)
            self.bot.message(target, 'Title: %s (at %s)' % (title, trueurl.split('/')[2]))
        except:
            pass
