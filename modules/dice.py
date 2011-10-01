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

import random
import re

class Dice(object):
    def __init__(self, bot, conf):
        self.conf = conf
        self.bot = bot
        
    def on_message(self, umask, target, msg):
        if msg.startswith("!dice "):
            msgsplit = msg.split()
            if msgsplit[1] == 'help':
                self.help(umask, target)
            elif 'd' in msgsplit[1]:
                self.dice(target, msgsplit[1], umask)
            else:
                self.bot.message(target, "Syntaxe incorrecte.")
                
    def dice(self, target, msg, umask):
        plus = 0
        dice = 0
        savemsg = msg
        diceslist = []
        if '+' in msg:
            msg = msg.split('+')
            try:
                plus = int(msg[1])
            except ValueError:
                self.bot.message(target, "%s: Valeur incorrect du bonus." % umask.nick)
                return
            if plus > 1000 or plus < -1000:
                self.help(umask, target)
                return
        else:
            msg = msg.split(' ')
        msgd = msg[0].split('d')
        if len(msgd) != 2:
            self.help(umask, target)
            return
        try:
            nbrdices = int(msgd[0])
        except ValueError:
            self.bot.message(target, "%s: nombre de dés incorrect." % umask.nick)
            return
        try:
            nbrfaces = int(msgd[1])
        except ValueError:
            self.bot.message(target, "%s: nombre de faces incorrect." % umask.nick)
            return
        if nbrdices < 1 or nbrfaces <= 0:
            self.bot.message(target, "%s: fu-." % umask.nick)
            return
        if nbrdices > 10 or nbrfaces > 100:
            self.help(umask, target)
            return
        for i in range(nbrdices):
            d = random.randint(1, nbrfaces)
            diceslist.append(d)
            dice += d
        dice += plus
        self.bot.message(target, "%s > %s : %i %s." % (umask.nick, savemsg, dice, diceslist))

    def help(self, umask, target):
        self.bot.message(target, "%s: Lancer un dé sur le modèle 1d20. Usage : !dice 6d6+3. Pas plus de 10 dés de 100 faces au maximum." % umask.nick)
