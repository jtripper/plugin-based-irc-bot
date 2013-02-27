#!/usr/bin/python
# encoding: utf-8

# main.py
# (C) 2013 jtRIPper
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 1, or (at your option)
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import os
import sys
import traceback
sys.path += ("irc", )
from pluginDriver import pluginDriver
from irc import IRC
from auth import auth
from config import *

bot = IRC(hostname, port, nickname, username, realname, use_ssl=ssl, use_proxy=proxy, proxy_host=proxy_host, proxy_port=proxy_port)
bot.raw("MODE %s +B" % nickname)
bot.join(channel)

driver = pluginDriver()
driver.load_plugins("plugins", bot)

authentication = auth(bot)
authentication.auth_levels[bot_master.lower()] = 10

while bot.connected == 1:
  buffer = bot.receive()
  if not buffer:
    continue

  for buf in buffer:
    if not buf:
      continue

    (tmp, auth_level) = authentication.check(bot, buf)
    if not tmp:
      continue

    try:
      ret = driver.run_command(tmp, auth_level, authentication, bot)
      if not ret:
        continue
      bot.msg(buf.to, ret)

    except Exception as e:
      exc_type, exc_value, exc_traceback = sys.exc_info()
      for err in traceback.extract_tb(exc_traceback, limit=10):
        print str(err)
      print str(type(e))
      print str(e)
