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
      sys.modules.pop(module)
      self.plugins.pop(module)
      bot.msg(buffer.to, "Unloaded: %s." % module)

    else:
      bot.msg(buffer.to, "Module not loaded.")

  def load_plugin(self, buffer, module, bot):
    #sys.path += (os.getcwd() + "/" + self.directory, )

    if module not in self.modules:
      self.modules += ( module, )
      self.plugins[module] = __import__(module).__dict__[module](bot)
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run[module] = self.plugins[module].__dict__["autorun"]

    else:
      sys.modules.pop(module)
      self.plugins[module] = __import__(module).__dict__[module](bot)
      if self.plugins[module].__dict__.has_key("autorun"):
        self.auto_run.pop(module)
        self.auto_run[module] = self.plugins[module].__dict__["autorun"]

    bot.msg(buffer.to, "Loaded: " + module)

  def load_plugins(self, directory, bot):
    self.directory = directory

    sys.path += (os.getcwd() + "/" + directory, )
    self.modules = ()
    for plugin in os.listdir(directory):
      if re.search(".py$", plugin):
        self.modules += ( plugin.rstrip(".py"), )

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

    if args[0] == "plugin.unload":
      self.unload_plugin(buffer, args[1], bot)

    elif args[0] == "auth.level":
      if len(args) == 2:
        if auth.auth_levels.has_key(args[1].lower()):
          bot.msg(buffer.to, "%s is level %s." % (args[1], auth.auth_levels[args[1].lower()]))
        else:
          bot.msg(buffer.to, "%s not set." % (args[1]))

      else:
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
      self.plugins[command[0]].help(None)
      return

    if self.plugins[command[0]].allowed_functions[command[1]] <= auth_level:
      getattr(self.plugins[command[0]], command[1])(buffer)

    return
