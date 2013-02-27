# auth.py
# (C) 2012 jtRIPper
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

import copy
import os
import pickle
import re

class auth:
  def __init__(self, bot):
    self.pending_command = {}
    self.services = 2

    bot.msg("nickserv", "status %s" % bot.nickname)

    while 1:
      buffer = bot.receive()
      if not buffer:
        continue
      for buff in buffer:
        if not buffer:
          continue

        if buff.type == "NOTICE" and buff.sender.lower() == "nickserv":
          if re.match("STATUS %s [0-9]+" % bot.nickname, buff.msg):
            self.services = 0
          else:
            self.services = 1
          break

        if buff.type == "401":
          self.services = -1
          break
      if self.services != 2:
        break
    try:
      os.stat("data")
    except:
      os.mkdir("data", 0700)

    try:
      self.auth_levels = pickle.load(open("data/auth.p", "r"))
    except:
      self.auth_levels = { }
      pickle.dump(self.auth_levels, open("data/auth.p", "w"))

  def auth(self, bot, buff):
    try:
      if bot.verify[buff.sender.lower()] == -1:
        self.pending_command[buff.sender.lower()] = None
        return None

      elif bot.verify[buff.sender.lower()] == 1:
        buff = copy.deepcopy(self.pending_command[buff.sender.lower()])
        self.pending_command[buff.sender.lower()] = None
        return buff

    except:
      if self.services == 1:
        bot.raw("whois %s\n" % buff.sender)
      else:
        bot.msg("nickserv", "status %s\n" % buff.sender)

      self.pending_command[buff.sender.lower()] = copy.deepcopy(buff)
      return None

  def check(self, bot, buff):
    if self.services == -1:
      if buff == None:
        return (None, 0)

      if self.auth_levels.has_key(buff.sender.lower()):
        return (buff, self.auth_levels[buff.sender.lower()])
      else:
        return (buff, 0)

    if (buff.type == "330" or buff.type == "318") and self.services == 1:
      if self.pending_command.has_key(buff.sender.lower()):

        if self.pending_command[buff.sender.lower()] is not None:
          buff = self.auth(bot, buff)

          if buff == None:
            return (None, 0)

          if self.auth_levels.has_key(buff.sender.lower()):
            return (buff, self.auth_levels[buff.sender.lower()])
          else:
            return (buff, 0)
      return (buff, 0)

    elif buff.type == "NOTICE" and self.services == 0:
      if buff.sender.lower() == "nickserv" and re.match("STATUS [^ ]+ 3", buff.msg):
        buff.sender = re.search("STATUS ([^ ]+) 3", buff.msg).group(1)
        bot.verify[buff.sender.lower()] = 1

        if self.pending_command.has_key(buff.sender.lower()):

          if self.pending_command[buff.sender.lower()] is not None:
            buff = self.auth(bot, buff)

            if buff == None:
              return (None, 0)

            if self.auth_levels.has_key(buff.sender.lower()):
              return (buff, self.auth_levels[buff.sender.lower()])
            else:
              return (buff, 0)
        return (buff, 0)

      elif buff.sender.lower() == "nickserv" and re.match("STATUS [^ ]+ [0-9]+", buff.msg):
        buff.sender = re.search("STATUS ([^ ]+) [0-9]+", buff.msg).group(1)
        bot.verify[buff.sender.lower()] = -1
        buff = self.auth(bot, buff)
        return (buff, 0)        

    elif buff.type == "PRIVMSG":
      if not bot.verify.has_key(buff.sender.lower()):
        buff = self.auth(bot, buff)
        return (buff, 0)

      else:
        if self.auth_levels.has_key(buff.sender.lower()) and bot.verify[buff.sender.lower()] == 1:
          return (buff, self.auth_levels[buff.sender.lower()])
        else:
          return (buff, 0)

    elif buff.type == "PART" or buff.type == "KICK" or buff.type == "QUIT" or buff.type == "NICK":
      if bot.verify.has_key(buff.sender.lower()):
        bot.verify.pop(buff.sender.lower())

    return (None, None)
