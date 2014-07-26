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
  def __init__(self):
    self.allowed_functions = { 'nick':10, 'join':10, 'part':10, 'quit':10, 'connect':10 }

  def nick(self, bot, sock, buffer):
    nick = buffer.msg.split()
    if len(nick) == 2:
      sock.nick(nick[1])

  def join(self, bot, sock, buffer):
    chan = buffer.msg.split()
    if len(chan) == 2:
      sock.join(chan[1])

  def part(self, bot, sock, buffer):
    chan = buffer.msg.split()
    if len(chan) == 2:
      sock.part(chan[1])
    else:
      if buffer.chan != None:
        sock.part(buffer.chan)

  def connect(self, bot, sock, buffer):
    buff = buffer.msg.split()

    hostname   = buff[1]
    port       = int(buff[2])
    nick       = buff[3]
    user       = buff[3]
    real       = buff[3]
    channel    = buff[4]
    use_ssl    = int(buff[5])
    proxy_host = "127.0.0.1"
    proxy_port = 9050
    use_proxy  = 0

    bot.connect(hostname, port, nick, user, real, channel, use_ssl=use_ssl, use_proxy=use_proxy, proxy_host=proxy_host, proxy_port=proxy_port)
    sock.msg(buffer.to, "Connecting to %s" % hostname)

  def quit(self, bot, sock, buffer):
    sock.disconnect()
    sock.reconnect = False

  def help(self, bot, sock, buffer):
    sock.msg(buffer.to, "Usage:")
    sock.msg(buffer.to, "  * control.nick <nickname>")
    sock.msg(buffer.to, "  * control.join <channel>")
    sock.msg(buffer.to, "  * control.quit")
