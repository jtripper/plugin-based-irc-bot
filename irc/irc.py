# -*- coding: utf-8 -*-
# irc.py
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

import socket
import re
import time
import struct
import tor
import ssl
import select
import config
import auth

class Message: # the Message class, this stores all the message information
  def __init__(self, buffer):
    self.raw    = buffer
    self.len    = len(buffer)
    self.type   = buffer[1]
    self.sender = buffer[0].split("!")[0][1:]
    self.ident  = buffer[0][1:]

    try:
      self.username = buffer[0].split("!")[1].split("@")[0]
      self.hostname = buffer[0].split("!")[1].split("@")[1]
    except:
      self.username = ""
      self.hostname = ""

    if buffer[2][0] == "#" and self.type == "PRIVMSG":
      self.chan = buffer[2].lower()
      self.to   = buffer[2].lower()

    elif self.type == "KICK":
      self.sender = buffer[3]
      self.chan   = buffer[2]
      self.to     = self.chan

    elif self.type == "PART":
      self.chan = buffer[2].rstrip().lower()
      self.to   = self.chan

    elif self.type == "JOIN":
      self.chan = buffer[2][1:].rstrip().lower()
      self.to   = self.chan

    elif self.type == "NICK":
      self.chan = None
      self.to   = self.sender
      self.msg  = ' '.join(buffer[2:])[1:].rstrip()

    elif self.type == "330" or self.type == "318" or self.type == "307":
      self.sender = buffer[3]
      self.chan   = None
      self.to     = self.sender

    elif self.type == "401":
      self.sender = buffer[2]
      self.chan   = None
      self.to     = buffer[3]

    else:
      self.chan  = None
      self.to    = self.sender

    if self.type == "NOTICE" or self.type == "PRIVMSG" or self.type == "QUIT" or self.type == "PART":
      self.msg    = ' '.join(buffer[3:])[1:].rstrip()

    else:
      try:
        self.msg
      except:
        self.msg = ""

class _IRC:
  def __init__(self, sock, hostname, nick, user, real, chan):
    self.nickname   = nick
    self.user       = user
    self.real       = real
    self.hostname   = hostname
    self.sock       = sock
    self.auth       = None

    self.verify = {}
    self.connected  = 0
    self.chan = [ chan ]

    self.nick(self.nickname)
    self.sock.send("USER %s %s %s :%s\n" % (self.user, self.user, self.user, self.real))

  def raw(self, buffer): # send a raw message
    self.sock.send("%s\n" % buffer)

  def disconnect(self): # quit
    self.sock.send("QUIT :https://github.com/jtRIPper/plugin-based-irc-bot\n")
    self.connected = 0

  def _join(self):
    for chan in self.chan:
      self.sock.send("JOIN %s\n" % chan)

  def join(self, chan): # join a channel
    self.sock.send("JOIN %s\n" % chan)
    self.chan.append(chan)

  def part(self, chan): # join a channel
    self.sock.send("PART %s\n" % chan)
    self.chan.remove(chan)

  def msg(self, to, buffer): # send a message
    lines = buffer.split('\n')
    for line in lines:
      for lin in re.findall(".?"*350, line):
        if lin != None and len(lin) > 0:
          self.sock.send(("PRIVMSG %s :%s\n" % (to, lin)))

  def notice(self, to, buffer): # send a notice
    lines = buffer.split('\n')
    for line in lines:
      for lin in re.findall(".?"*350, line):
        if lin != None and len(lin) > 0:
          self.sock.send(("NOTICE %s :%s\n" % (to, lin)).encode('utf-8'))
          time.sleep(1)

  def ctcp(self, to, buffer): # send a ctcp message
    self.sock.send("PRIVMSG %s :\001%s\001\n"% (to, buffer))

  def nick(self, nick): # change nick
    self.sock.send("NICK %s\n" % nick)
    self.nickname = nick

  def parse(self, buffer): # parse the messages
    buffer = buffer.split()
    length = len(buffer)

    if length > 0 and buffer[0] == "PING":
      self.ping(buffer)

    elif length > 1 and (buffer[1] == "376" or "/MOTD" in ' '.join(buffer)):
      self.connected = 1
      self._join()
      self.auth = auth.auth(self)
      self.auth.auth_levels[config.bot_master.lower()] = 10

    elif length > 1 and buffer[1] == "330":
      if "is logged in as" in ' '.join(buffer):
        self.verify[buffer[3].lower()] = 1
      return Message(buffer)

    elif length > 1 and buffer[1] == "307":
      if "is identified for this nick" in ' '.join(buffer):
        self.verify[buffer[3].lower()] = 1
      if "is a registered nick" in ' '.join(buffer):
        self.verify[buffer[3].lower()] = 1
      return Message(buffer)

    elif length > 1 and buffer[1] == "318":
      try:
        if self.verify[buffer[3].lower()] != 1:
          self.verify[buffer[3].lower()] = -1
      except:
        self.verify[buffer[3].lower()] = -1
      return Message(buffer)

    elif length > 1 and buffer[1] == "401":
      return Message(buffer)

    elif length > 2 and (buffer[1] == "PRIVMSG" or buffer[1] == "NOTICE"
        or buffer[1] == "JOIN" or buffer[1] == "PART" or buffer[1] == "QUIT"
        or buffer[1] == "NICK" or buffer[1] == "KICK"):
      return Message(buffer)

    return None

  def receive(self, buffer): # receive a message
    print(buffer.rstrip())

    if len(buffer.split('\n')) > 1:
      rets = ()

      for buff in buffer.split('\n'):
        ret = self.parse(buff)

        if ret != None:
          rets += (ret, )

      return rets

    else:
      return (self.parse(buffer), )

  def check(self, buffer):
    return self.auth.check(self, buffer)

  def ping(self, buffer): # reply to a ping
    self.sock.send(re.sub("PING", "PONG", ' '.join(buffer)) + "\n")

  def recv(self, size):
    return self.sock.recv(size)

  def fileno(self):
    return self.sock.fileno()

class IRC:
  def __init__(self):
    self.socks = []
    self.ircs  = {}

    self.buffers = {}

  def connect(self, hostname, port, nick, user, real, chan, use_proxy=0, proxy_host=None, proxy_port=None, use_ssl=0):
    if use_proxy:
      s = tor.AsyncSocksSocket(tor_host=proxy_host, tor_port=proxy_port, use_ssl=use_ssl)
      s.connect((hostname, port))
      self.ircs[s] = [hostname, nick, user, real, chan]
      self.socks.append(s)
    else:
      s = socket.socket()
      s.connect((hostname, port))
      if use_ssl:
        s = ssl.wrap_socket(s)
      self.socks.append(_IRC(s, hostname, nick, user, real, chan))

  def _receive(self):
    readable, writable, exceptional = select.select(self.socks, [], [])

    for s in readable:
      try:
        data = s.recv(1024)
      except socket.error:
        self.socks.remove(s)
        continue

      if data == "" or not data:
        self.socks.remove(s)
        continue

      if s not in self.buffers:
        self.buffers[s] = data
      else:
        self.buffers[s] += data

      buff = self.buffers[s].split("\r\n")
      self.buffers[s] = buff[-1]
      yield s, "\r\n".join(buff[:-1])

  def receive(self):
    for s, data in self._receive():
      if not data:
        continue

      if isinstance(s, tor.AsyncSocksSocket) and s.connected:
        self.socks.remove(s)
        self.socks.append(_IRC(s, self.ircs[s][0], self.ircs[s][1], self.ircs[s][2], self.ircs[s][3], self.ircs[s][4]))

      elif isinstance(s, _IRC) and not s.connected:
        s.receive(data)

      elif isinstance(s, _IRC):
        return [s, s.receive(data)]
