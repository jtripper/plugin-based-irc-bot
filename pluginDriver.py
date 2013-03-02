# pluginDriver.py
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

import sys
import os
import re
import pickle

class pluginDriver:
  def __init__(self):
    pass

  def unload_plugin(self, buffer, module, bot):
    if module in self.modules:
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run.pop(module)
      self.plugins.pop(module)
      sys.modules.pop(module)
      self.modules.remove(module)
      bot.msg(buffer.to, "Unloaded: %s." % module)

    else:
      bot.msg(buffer.to, "Module not loaded.")

  def load_plugin(self, buffer, module, bot):
    if module not in self.modules:
      self.modules.append(module)
      self.plugins[module] = __import__(module).__dict__[module](bot)
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run[module] = self.plugins[module].__dict__["autorun"]

    else:
      self.modules.remove(module)
      sys.modules.pop(module)
      self.plugins[module] = __import__(module).__dict__[module](bot)
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run.pop(module)
        self.auto_run[module] = self.plugins[module].__dict__["autorun"]
      self.modules.append(module)

    bot.msg(buffer.to, "Loaded: " + module)

  def load_plugins(self, directory, bot):
    self.directory = directory

    sys.path += (os.getcwd() + "/" + directory, )
    self.modules = []
    for plugin in os.listdir(directory):
      if re.search(".py$", plugin):
        self.modules.append(re.sub("\.py$", "", plugin))

    self.plugins = {}
    self.auto_run = {}

    for module in self.modules:
      self.plugins[module] = __import__(module).__dict__[module](bot)
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run[module] = self.plugins[module].__dict__["autorun"]

  def meta_commands(self, buffer, auth_level, auth, args, command, bot):
    if auth_level != 10:
      return

    if args[0] == "plugin.load":
      self.load_plugin(buffer, args[1], bot)

    elif args[0] == "plugin.unload":
      self.unload_plugin(buffer, args[1], bot)

    elif args[0] == "plugin.list":
      bot.msg(buffer.to, "Loaded modules:")
      for module in self.modules:
        bot.msg(buffer.to, " * %s" % module)

    elif args[0] == "auth.levels":
      bot.msg(buffer.to, "Auth levels:")
      for level in auth.auth_levels:
        bot.msg(buffer.to, " * %s -- %d" % (level, auth.auth_levels[level]))

    elif args[0] == "auth.level":
      if len(args) == 2:
        if auth.auth_levels.has_key(args[1].lower()):
          bot.msg(buffer.to, "%s is level %s." % (args[1], auth.auth_levels[args[1].lower()]))
        else:
          bot.msg(buffer.to, "%s not set." % (args[1]))

      elif len(args) == 3:
        auth.auth_levels[args[1].lower()] = int(args[2])
        bot.msg(buffer.to, "Set %s to level %s." % (args[1], args[2]))
        pickle.dump(auth.auth_levels, open("data/auth.p", "w"))

  def run_command(self, buffer, auth_level, auth, bot):
    if not buffer.msg:
      return

    for module in self.auto_run:
      self.auto_run[module](auth_level, buffer)

    args = buffer.msg.split()
    command = args[0].split(".")

    if len(command) != 2:
      return

    if command[0] not in self.plugins:
      self.meta_commands(buffer, auth_level, auth, args, command, bot)
      return

    if command[1] not in self.plugins[command[0]].allowed_functions:
      self.plugins[command[0]].help(buffer)
      return

    if self.plugins[command[0]].allowed_functions[command[1]] <= auth_level:
      getattr(self.plugins[command[0]], command[1])(buffer)

    return
