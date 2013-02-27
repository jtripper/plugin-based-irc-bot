# control.py
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

class control:
  def __init__(self, bot):
    self.allowed_functions = { 'nick':10, 'join':10, 'part':10, 'quit':10 }
    self.bot = bot

  def nick(self, buffer):
    nick = buffer.msg.split()
    if len(nick) == 2:
      self.bot.nick(nick[1])

  def join(self, buffer):
    chan = buffer.msg.split()
    if len(chan) == 2:
      self.bot.join(chan[1])

  def part(self, buffer):
    chan = buffer.msg.split()
    if len(chan) == 2:
      self.bot.part(chan[1])
    else:
      if buffer.chan != None:
        self.bot.part(buffer.chan)

  def quit(self, buffer):
    self.bot.disconnect()

  def help(self, buffer):
    self.bot.msg(buffer.to, "Usage:")
    self.bot.msg(buffer.to, "  * control.nick <nickname>")
    self.bot.msg(buffer.to, "  * control.join <channel>")
    self.bot.msg(buffer.to, "  * control.quit")
