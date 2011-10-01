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
import os
import re

class Quote(object):
    """ Classe pour le bot Yppy destinée à permet l'ajout de citations """
    def __init__(self, bot, conf):
        self.conf = conf
        self.bot = bot
        self.old = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.oldlist = {}
        self.link = ""
        self.fd = ""

    def on_message(self, umask, target, msg):
        chan = target.replace('#', '').lower()
        print (self.conf)
        self.link = self.conf['linkfile'] + '/' + self.conf['host'] + "-" + chan + ".quote"
        msgsplit = msg.split(' ')
        if msgsplit[0] == "!quote" and len(msgsplit) <= 1:
            self.affrandom(target)
            return
        if msgsplit[0] == "!quote":
            if msgsplit[1] == "add":
                self.add(umask, target, msg)
            elif msgsplit[1] == "list":
                self.list(target)
            elif msgsplit[1] == "id":
                self.affid(target, msgsplit, -1)
            elif msgsplit[1] == "del":
                self.delete(umask, target, msgsplit)
            elif msgsplit[1] == "help":
                self.help(target, msgsplit)
            else:
                try:
                    msgid = int(msgsplit[1])
                    self.affid(target, msgsplit, msgid)
                except ValueError:
                    self.affrandom(target)
        return

    def openfile(self, mode="r"):
        try:
            self.fd = open(self.link, mode)
        except IOError:
            print("Module Quote, can't open file %s" % self.link)
            return False
        return True

    def closefile(self):
        self.fd.close()

    def add(self, umask, target, msg):
        """ Ajouter une nouvelle citation """
        if len(msg) <= 11:
            return
        try:
            if os.path.isfile(self.link):
                fd = open(self.link , "r")
            else:
                fd = open(self.link , "a+")
        except IOError:
            print("Module Quote, add, can't open file %s" % self.link)
            return
        lines = fd.readlines()
        fd.close()
        num = len(lines) + 1
        if num != 1:
            oldid = int(lines[num - 2].split()[0])
        else:
            oldid = 0
        if  oldid != num - 1:
            num = oldid + 1
        if not self.openfile("a"):
            return
        self.fd.write("%i %s (added by %s)\n" % (num, msg[11:], umask.nick))
        self.closefile()
        self.bot.message(target, "citation ajoutée")

    def idlog(self, target, line):
        """ Log les dernieres citations postees sur le chan """
        if not slef.oldlist.has_key(target):
            self.oldlist[target] = self.old
        self.oldlist[target].append(line)
        self.oldlist[target].pop(0)

    def idsearch(self, target, line):
        """ Verfie si la citation fait partie des 10 dernieres envoyees """
        if slef.oldlist.has_key(target):
            if line in slef.oldlist[target]:
                return True
        return False

    def affid(self, target, msgsplit, msgid):
        """ Affichier une citation a partir de son id """
        if not self.openfile():
            return
        quotes = self.fd.readlines()
        if msgid == -1:
            try:
                msgid = int(msgsplit[2])
            except ValueError:
                return
            except IndexError:
                msgid = -1
        if msgid < 1 or msgid > len(quotes):
            self.bot.message(target, "id incorrect")
            return
        self.aff(target, msgid, quotes)

    def affrandom(self, target):
        """ Afficher une citation au hasard """
        line = -1
        if not self.openfile():
            return
        quotes = self.fd.readlines()
        if len(quotes) > 1:
            while line == -1:
                line = random.randint(0, len(quotes) - 1)
                if self.idsearch(target, line) and len(quotes) > len(self.old):
                    line = -1
            self.idlog(target, line)
            self.aff(target, line, quotes)

    def aff(self, target, msgid, quotes):
        """ Afficher la citation """
        l = quotes[msgid - 1].split()
        tmpi = len(l[0]) + 1
        self.bot.message(target, "%s" % (quotes[msgid - 1][tmpi:]))
        self.fd.close()

    def list(self, target):
        """ Afficher le lien du fichier contenant toutes les citations """
        self.bot.message(target, "http://docs.khady.info/%s.quote" % (self.conf['host'] + '-' + target.lower()))

    def delete(self, umask, target, msgsplit):
        """ Supprimer une citation du fichier a partir de l'id passé dans le message"""
        if umask.nick not in self.conf['channels']['\\' + target.lower()]['op']:
            self.bot.message(target, "Désolé, vous n'avez pas les droits nécessaire pour cette action")
            return
        if len(msgsplit) <= 2 or not re.match(r'[0-9]*', msgsplit[2]):
            self.bot.message(target, "Vous devez préciser un ID correct")
            return
        msgid = int(msgsplit[2])
        if not self.openfile():
            return
        quotes = self.fd.readlines()
        self.fd.close()
        nquotes = []
        for quote in quotes:
            if int(quote.split()[0]) != msgid:
                nquotes.append(quote)
        if not self.openfile("w"):
            return
        for qts in nquotes:
            self.fd.write(qts)
        self.fd.close()

    def help(self, target, msgsplit):
        """ Afficher l'aide """
        l = len(msgsplit)
        if l == 2:
            self.bot.message(target, "!quote [add|del|list|help] [message]")
        else:
            if msgsplit[2] == 'add':
                self.bot.message(target, "Ajouter une nouvelle citation. Usage : !quote add message")
            elif msgsplit[2] == 'del':
                self.bot.message(target, "Supprimer une citation. Usage : !quote del id")
            elif msgsplit[2] == 'list':
                self.bot.message(target, "Afficher toutes les citations. Usage : !quote list")
            elif msgsplit[2] == 'help':
                self.bot.message(target, "Afficher l'aide globale ou d'une fonction. Usage : !quote help [fonction]")
            else:
                self.bot.message(target, "!quote [add|del|list|help] [message]")
