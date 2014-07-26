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
import importlib

class pluginDriver:
  def __init__(self):
    self.plugins = {}
    self.auto_run = {}

  def unload_plugin(self, plugin_name):
    if plugin_name in self.plugins:
      if plugin_name in self.auto_run:
        self.auto_run.pop(plugin_name)

      del sys.modules['plugins.' + plugin_name]
      del self.plugins[plugin_name]

      if bot:
        bot.msg(buffer.to, "Unloaded: %s." % plugin)
    else:
      if bot:
        bot.msg(buffer.to, "Module not loaded.")

  def load_plugin(self, plugin_name, bot=None, buffer=None):
    if plugin_name == '__init__':
      return

    if os.path.isfile("plugins/%s.py" % (plugin_name)):
      if plugin_name in self.plugins:
        self.unload_plugin(plugin_name)

      plugin = importlib.import_module('plugins.' + plugin_name)
      plugin = getattr(plugin, plugin_name)()

      self.plugins[plugin_name] = plugin
      if hasattr(plugin, "autorun"):
        self.auto_run[plugin_name] = getattr(plugin, "autorun")

      if bot:
        bot.msg(buffer.to, "Loaded: " + plugin_name)
    else:
      if bot:
        bot.msg(buffer.to, "Plugin does not exist.")

  def load_plugins(self):
    for plugin in os.listdir('plugins'):
      if not re.search(".py$", plugin):
        continue

      self.load_plugin(re.sub("\.py$", "", plugin))

  def meta_commands(self, buffer, auth_level, args, command, bot):
    if auth_level != 10:
      return

    if args[0] == "plugin.load" or args[0] == "plugin.reload":
      self.load_plugin(args[1], bot, buffer)

    elif args[0] == "plugin.unload":
      self.unload_plugin(args[1], bot, buffer)

    elif args[0] == "plugin.list":
      bot.msg(buffer.to, "Loaded plugins:")
      for plugin in self.plugins:
        bot.msg(buffer.to, " * %s" % plugin)

    elif args[0] == "auth.levels":
      bot.msg(buffer.to, "Auth levels:")
      for level in bot.auth.auth_levels:
        bot.msg(buffer.to, " * %s -- %d" % (level, bot.auth.auth_levels[level]))

    elif args[0] == "auth.level":
      if len(args) == 2:
        if bot.auth.auth_levels.has_key(args[1].lower()):
          bot.msg(buffer.to, "%s is level %s." % (args[1], bot.auth.auth_levels[args[1].lower()]))
        else:
          bot.msg(buffer.to, "%s not set." % (args[1]))

      elif len(args) == 3:
        bot.auth.auth_levels[args[1].lower()] = int(args[2])
        bot.msg(buffer.to, "Set %s to level %s." % (args[1], args[2]))
        pickle.dump(bot.auth.auth_levels, open("data/auth_%s.p" % bot.hostname, "w"))

  def run_command(self, bot, buffer, auth_level, sock):
    if not buffer.msg:
      return

    for plugin in self.auto_run:
      self.auto_run[plugin](bot, sock, auth_level, buffer)

    args = buffer.msg.split()
    command = args[0].split(".")

    if len(command) != 2:
      return

    if command[0] not in self.plugins:
      self.meta_commands(buffer, auth_level, args, command, sock)
      return

    if command[1] not in self.plugins[command[0]].allowed_functions:
      self.plugins[command[0]].help(bot, sock, buffer)
      return

    if self.plugins[command[0]].allowed_functions[command[1]] <= auth_level:
      getattr(self.plugins[command[0]], command[1])(bot, sock, buffer)

    return
