#!/usr/bin/python2
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
import config
import time

def init(bot):
  bot.connect(config.hostname, config.port, config.nickname, config.username,
    config.realname, config.channel, use_ssl=config.ssl, use_proxy=config.proxy,
    proxy_host=config.proxy_host, proxy_port=config.proxy_port)

  driver = pluginDriver()
  driver.load_plugins()

  return driver

bot = IRC()
driver = init(bot)

while bot.socks != []:
  for sock, buffer in bot.receive():
    if not buffer:
      if sock.reconnect:
        driver.unload_plugins()
        time.sleep(2)
        driver = init(bot)
      continue

    for buf in buffer:
      if not buf:
        continue

      (tmp, auth_level) = sock.check(buf)
      if not tmp:
        continue

      try:
        ret = driver.run_command(bot, tmp, auth_level, sock)
        if not ret:
          continue
        sock.msg(buf.to, ret)

      except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        for err in traceback.extract_tb(exc_traceback, limit=10):
          print(err)
        print(type(e))
        print(e)


