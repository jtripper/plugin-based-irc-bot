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

import socket, socks, re, time

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

    elif self.type == "330" or self.type == "318":
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

class IRC:
  def __init__(self, hostname, port, nick, user, real, use_proxy=0, proxy_host=None, proxy_port=None, use_ssl=0):
    self.hostname   = hostname
    self.port       = int(port)

    self.nickname   = nick
    self.user       = user
    self.real       = real

    self.use_proxy  = use_proxy
    self.proxy_host = proxy_host

    if proxy_port != None:
      self.proxy_port = int(proxy_port)

    self.use_ssl    = use_ssl

    self.verify = {}
    self.connected  = 0
    self.chan = []

    self.connect()

  def connect(self): # connect() to the ircd
    if self.use_proxy == 1 and self.use_ssl == 1:
      print "Error: Cannot use both ssl and a proxy!"
      exit()

    if self.use_proxy == 1:
      self.sock = socks.socksocket()
      self.sock.setproxy(socks.PROXY_TYPE_SOCKS5, self.proxy_host, self.proxy_port)
    else:
      self.sock = socket.socket()

    if self.use_ssl == 1:
      import ssl
      self.sock = ssl.wrap_socket(self.sock)
 
    self.sock.connect((self.hostname, self.port))

    self.nick(self.nickname)
    self.sock.send("USER %s %s %s :%s\n" % (self.user, self.user, self.user, self.real))

    while self.connected != 1:
      self.receive()

  def raw(self, buffer): # send a raw message
    self.sock.send("%s\n" % buffer)

  def disconnect(self): # quit
    self.sock.send("QUIT :I ask for rich guy stuff and you give me shiny pebbles?! I bid you, adieu!\n")
    self.connected = 0
 
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
          self.sock.send(("PRIVMSG %s :%s\n" % (to, lin)).encode('utf-8'))
          time.sleep(1)

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

    elif length > 1 and buffer[1] == "376":
      self.connected = 1

    elif length > 1 and buffer[1] == "330":
      if "is logged in as" in ' '.join(buffer):
        self.verify[buffer[3]] = 1
      return Message(buffer)

    elif length > 1 and buffer[1] == "318":
      try:
        if self.verify[buffer[3]] != 1:
          self.verify[buffer[3]] = -1
      except:
        self.verify[buffer[3]] = -1
      return Message(buffer)

    elif length > 1 and buffer[1] == "401":
      return Message(buffer)
        
    elif length > 2 and (buffer[1] == "PRIVMSG" or buffer[1] == "NOTICE" or buffer[1] == "JOIN" or buffer[1] == "PART" or buffer[1] == "QUIT" or buffer[1] == "NICK" or buffer[1] == "KICK"):
      return Message(buffer)

    return None

  def receive(self): # receive a message
    buffer = self.sock.recv(1024)
    print buffer.rstrip()

    if len(buffer.split('\n')) > 1:
      rets = ()

      for buff in buffer.split('\n'):
        ret = self.parse(buff)

        if ret != None:
          rets += (ret, )

      return rets

    else:
      return (self.parse(buffer), )

  def ping(self, buffer): # reply to a ping
    self.sock.send(re.sub("PING", "PONG", ' '.join(buffer)) + "\n")

