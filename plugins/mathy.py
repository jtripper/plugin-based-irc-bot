#!/usr/bin/python2
# -*- coding: utf8 -*-

"""
Simple math plugin for the Plugin-based IRC Bot
Example usage: mathy.solve 1+3

(C) 2014 Norwack (https://github.com/norwack)

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 1, or (at your option)
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import re

class mathy:
  def __init__(self):
    self.allowed_functions = { 'solve': 0, 'help': 0 }
  
  def solve(self, bot, sock, buffer):
    args = buffer.msg.split()
    if len(args) == 2:
      regex = "([-+]?[0-9]*\.?[0-9]+[\/\+\-\*])+([-+]?[0-9]*\.?[0-9]+)"
      if re.match(regex, args[1]):
        math_result = int(eval(args[1]))
        sock.msg(buffer.to, "* Result: 03%s = %s" % (args[1], math_result))
      else:
        self.help(bot, sock, buffer)
    else:
      self.help(bot, sock, buffer)
  
  def help(self, bot, sock, buffer):
    sock.msg(buffer.to, "Usage:")
    sock.msg(buffer.to, "  mathy.solve  <math problem> | Example: 3+3/2")