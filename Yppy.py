#!/usr/bin/env python3.2
#-*- encoding: utf-8 -*-

# Copyright (c) 2010, 2011 Mick@el and Zopieux and Louis Roché and Pierre-Jean Prost
#
# pypeul is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# pypeul is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with pypeul. If not, see <http://www.gnu.org/licenses/>.

import sys
import yaml
import threading
from pypeul import *
from imp import reload

class ModuleNotFound(Exception): pass

class Yppy(IRC):
    def on_ready(self):
        for chan in self.conf['channels']:
            self.join(chan[1:])

    def on_message(self, umask, target, msg):
        if umask.nick in self.conf['channels']["\\" + target.lower()]['op']:
            op = 1
        else:
            op = 0

        try:
            if msg.startswith('!load ') and op == 1:
                for modname in map(str.lower, msg[6:].split()):
                    if not modname:
                        continue
                    try:
                        self.load_module(modname)
                        self.message(target, 'Module %s (re)loaded.' % Tags.Bold(modname))
                    except ModuleNotFound:
                        self.message(target, 'Module %s not found.' % Tags.Bold(modname))

            elif msg.startswith('!unload ') and op == 1:
                for modname in map(str.lower, msg[8:].split()):
                    if not modname:
                        continue
                    try:
                        self.unload_module(modname)
                        self.message(target, 'Module %s unloaded.' % Tags.Bold(modname))
                    except ModuleNotFound:
                        self.message(target, 'Module %s not found.' % Tags.Bold(modname))
            else:
                if op == 0:
                    return

        except Exception as ex:
            self.message(target, Tags.Bold('Exception : ') + repr(ex))
            raise

    def on_ctcp_ping_request(self, umask, value):
        self.ctcp_reply(umask.nick, 'PING', value)

    def on_ctcp_version_request(self, umask, value):
        self.ctcp_reply(umask.nick, 'VERSION', sys.modules['pypeul'].__version__)

    def nick_guess(self, part, channel):
        """
        Useful function that returns a list of 0, 1 or several possible users
        """
        return [user for lnick, user in self.users.items() if irc_lower(part) in lnick and channel in user.channels]

    def load_module(self, modname):
        modname = modname.lower()

        try:
            if modname in self.handlers:
                module = reload(sys.modules['modules.' + modname])
            else:
                module = getattr(__import__('modules.' + modname), modname)

            self.handlers[modname] = getattr(module, modname.title())(self, self.conf)
        except ImportError:
            raise ModuleNotFound

    def unload_module(self, modname):
        modname = modname.lower()

        try:
            del sys.modules['modules.' + modname]
            del self.handlers[modname]
        except KeyError:
            raise ModuleNotFound

    def reload_modules(self):
        for modname in self.modules:
            try:
                self.load_module(modname)
                print ('@ Module %s (re)loaded.' % Tags.Bold(modname))
            except ModuleNotFound:
                print ('@ Module %s not found.' % Tags.Bold(modname))

class _ThreadBot(threading.Thread):
    def __init__(self, conf):
        threading.Thread.__init__(self)
        self.conf = conf

    def run(self):
        bot = Yppy()
        bot.conf = self.conf
        bot.modules = self.conf['modules']
        bot.connect(self.conf['host'], int(self.conf['port']))
        bot.ident(self.conf['nickname'])
        bot.reload_modules()
        bot.run()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ("Usage: %s <config.yml>" % sys.argv[0])
        sys.exit()

    try:
        fd = open(sys.argv[1],'r')
    except IOError:
        print ("%s: No such file, or permission is denied." % sys.argv[1])
        sys.exit()
    yaml_content = fd.read()
    fd.close()
    conf = yaml.load(yaml_content)

    for server in conf.keys():
        thread = _ThreadBot(conf[server])
        thread.start()
