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

class Modadmin(object):
    def __init__(self, bot, conf):
        self.conf = conf
        self.bot = bot
        self.source = "http://h.khady.info/index.php/p/lepers"

    def on_message(self, umask, target, msg):
        if msg.startswith("!ping"):
            self.bot.message(target, "pong")

        if umask.nick not in self.conf['channels']['\\' + target.lower()]['op']:
            return

        if msg.startswith("!topic "):
            self.bot.topic(target, msg[7:])
            return
        
        if msg.startswith("!op"):
            msg = msg.split(" ")
            if len(msg) > 1:
                self.bot.set_modes(target, ('+o', msg[1]))
            else:
                self.bot.set_modes(target, ('+o', umask.nick))
            return

        if msg.startswith("!deop"):
            msg = msg.split(" ")
            if len(msg) > 1:
                self.bot.set_modes(target, ('-o', msg[1]))
            else:
                self.bot.set_modes(target, ('-o', umask.nick))
            return

        if msg.startswith("!kick "):
            msg = msg.split(" ")
            if msg[1] == self.conf['nickname']:
                return
            if len(msg) == 2:
                self.bot.kick(target, msg[1], 'kick by %s' % umask.nick)
            else:
                self.bot.kick(target, msg[1], 'kick by %s: %s' % (umask.nick, msg[2]))            
            return

        if msg.startswith("!ban "):
            msg = msg.split(" ")
            self.bot.set_modes(target, ('+b', msg[1]))

        if msg.startswith("!unban "):
            msg = msg.split(" ")
            self.bot.set_modes(target, ('-b', msg[1]))

        if msg.startswith("!die ") or msg == "!die":
            quitmsg = "NOOOOOOOOOOOOOOOOOOOOOON"
            if len(msg) > 4:
                quitmsg = msg[5:]
            self.bot.quit(quitmsg)
            return
            
        if msg.startswith("!source"):
            self.bot.message(target, self.source)

    def on_server_kick(self, umask, channel, kicked_nick, reason=None):
        if kicked_nick == self.conf['nickname']:
            self.bot.join(channel)

    def on_disconnect(self):
        self.bot.connected == False
        while self.bot.connected == False:
            time.sleep(5)
            self.bot.connect(self.conf['host'], int(self.conf['port']))
