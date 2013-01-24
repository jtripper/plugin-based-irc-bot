#!/usr/bin/python2
# coding: utf-8

import os
import sys
import traceback
sys.path += ("irc", )
from pluginDriver import pluginDriver
from irc import IRC
from auth import auth

bot = IRC("irc.com", 6697, "lol", "lol", "lol", use_ssl=1)
bot.raw("MODE lol +B")
bot.join("#bot")

driver = pluginDriver()
driver.load_plugins("plugins", bot)

authentication = auth()

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