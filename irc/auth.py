import copy
import os
import pickle

class auth:
  def __init__(self):
    self.pending_command = {}

    try:
      os.stat("data")
    except:
      os.mkdir("data", 0700)

    try:
      self.auth_levels = pickle.load(open("data/auth.p", "r"))
    except:
      self.auth_levels = { 'lol':10 }
      pickle.dump(self.auth_levels, open("data/auth.p", "w"))

  def auth(self, bot, buff):
    try:
      if bot.verify[buff.sender] == -1:
        self.pending_command[buff.sender] = None
        return None

      elif bot.verify[buff.sender] == 1:
        buff = copy.deepcopy(self.pending_command[buff.sender])
        self.pending_command[buff.sender] = None
        return buff

    except:
      bot.raw("whois %s\n" % buff.sender)
      self.pending_command[buff.sender] = copy.deepcopy(buff)
      return None

  def check(self, bot, buff):
    if buff.type == "330" or buff.type == "318":
      if self.pending_command.has_key(buff.sender):

        if self.pending_command[buff.sender] is not None:
          buff = self.auth(bot, buff)

          if buff == None:
            return (None, 0)

          if self.auth_levels.has_key(buff.sender.lower()):
            return (buff, self.auth_levels[buff.sender.lower()])
          else:
            return (buff, 0)
      return (buff, 0)

    elif buff.type == "PRIVMSG":
      if not bot.verify.has_key(buff.sender):
        buff = self.auth(bot, buff)
        return (buff, 0)

      else:
        if self.auth_levels.has_key(buff.sender.lower()) and bot.verify[buff.sender] == 1:
          return (buff, self.auth_levels[buff.sender.lower()])
        else:
          return (buff, 0)

    else:
      return (None, None)
