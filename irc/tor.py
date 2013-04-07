#   tor.py
#   (C) 2013 jtripper
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 1, or (at your option)
#   any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

import socket
def_socket = socket.socket
import struct
import os
import subprocess
import signal
import shutil
import time
import ssl

socks_host = ""
socks_port = 0

def set_socks_proxy(new_socks_host, new_socks_port):
  global socks_host
  global socks_port

  socks_host = new_socks_host
  socks_port = int(new_socks_port)

class TorError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

class Tor:
  def __init__(self, tor_instance_number):
    self.tor_host     = "127.0.0.1"
    self.tor_port     = 9052 + tor_instance_number

    set_socks_proxy(self.tor_host, self.tor_port)

    self.control_host = "127.0.0.1"
    self.control_port = 10052 + tor_instance_number
    self.tor_instance_number = tor_instance_number
    self.torrc        = ""

    self.tor_dir      = "%s/.tor%d" % (os.getcwd(), self.tor_instance_number)

    self.has_hidden_service = False
    self.hidden_service_hostname = ""

  # Restart this tor instance
  def restart_tor(self):
    self.tor.kill()
    self.create_tor()

  # Kill this tor instance and remove the data directory
  def kill_tor(self):
    self.tor.kill()

  # Cleanup tor directory
  def cleanup(self):
    shutil.rmtree(self.tor_dir, ignore_errors=True)

  # Create new tor instance (write out simple configuration and then run in background)
  def create_tor(self):
    self.append_to_torrc("SocksPort %d\n" % self.tor_port)
    self.append_to_torrc("RunAsDaemon 0\n")
    self.append_to_torrc("DataDirectory %s\n" % self.tor_dir)
    self.append_to_torrc("ControlPort %d\n" % self.control_port)

    try:
      os.mkdir(".tor%d" % self.tor_dir, 0700)
    except:
      pass

    torrc_handle = open(".%s/torrc" % self.tor_dir, "w")
    torrc_handle.write(self.torrc)
    torrc_handle.close()

    self.tor = subprocess.Popen("tor -f %s/torrc" % self.tor_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    time.sleep(0.5)

    if self.tor.poll():
      for line in self.tor.stdout.read().split("\n"):
        if "err" in line:
          raise TorError(line)

    if self.has_hidden_service:
      f = open("%s/hidden_service/hostname" % self.tor_dir)
      hostname = f.readlines()
      self.hidden_service_hostname = hostname[0].rstrip()
      f.close()

  def read_from_tor_proc(self):
    return self.tor.stdout.read()

  # Tor control port handler
  def torctl(self, command="", password=""):
    s = def_socket()
    s.connect((self.control_host, self.control_port))

    s.send("Authenticate %s\r\n" % password)
    if "250" not in s.recv(1024):
      return -1

    s.send("%s\r\n" % command)
    if "250" not in s.recv(1024):
      return -1

    s.close()

  # Signal newnym
  def newnym(self):
    return self.torctl(command="signal newnym")

  # Start a hidden service
  def hidden_service(self, listen_port, forward_port=None):
    if not forward_port: forward_port = listen_port

    self.append_to_torrc("HiddenServiceDir %s/hidden_service/" % (self.tor_dir))
    self.append_to_torrc("HiddenServicePort %d 127.0.0.1:%d" % (listen_port, forward_port))

    self.has_hidden_service = True

  # Append line to torrc
  def append_to_torrc(self, line):
    self.torrc += "%s\n" % line

  # Check tor with check.torproject.org
  def verify_tor(self):
    socket.socket = SocksSocket
    import urllib
    data = urllib.urlopen("http://check.torproject.org/").read()

    if "Congratulations" in data:
      return True
    else:
      return False

# Socks socket wrapper
class SocksSocket(socket.socket):
  def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, tor_host=None, tor_port=None):
    def_socket.__init__(self, family, type, proto)

    if not tor_host:
      self.tor_host = socks_host
    else:
      self.tor_host = tor_host

    if not tor_port:
      self.tor_port = socks_port
    else:
      self.tor_port = tor_port

  # Negotiate socks
  def connect(self, (host, port)):
    def_socket.connect(self, (self.tor_host, self.tor_port))

    self.send("\x05\x01\x00")

    if self.recv(2) != "\x05\x00":
      raise socket.error

    port   = struct.pack("!H", port)
    length = chr(len(host))

    self.send(("\x05\x01\x00\x03%s%s%s" % (length, host, port)))

    if self.recv(10) != "\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00":
      raise socket.error("Connection refused.")

class AsyncSocksSocket:
  def __init__(self, tor_host=None, tor_port=None, use_ssl=0):
    self._sock = def_socket()
    self.ssl = use_ssl

    self.connected   = False
    self.negotiation = 0
    self.send_ok     = 0

    self.send_queue = []

    if not tor_host:
      self.tor_host = socks_host
    else:
      self.tor_host = tor_host

    if not tor_port:
      self.tor_port = socks_port
    else:
      self.tor_port = tor_port

  # Negotiate socks
  def connect(self, (host, port)):
    self._sock.connect((self.tor_host, self.tor_port))

    self.port = int(port)
    self.host = host

    self.send_ok = 1
    self.send("\x05\x01\x00")
    self.send_ok = 0

  def recv(self, size):
    data = self._sock.recv(size)

    if self.negotiation == 0:
      if data != "\x05\x00":
        raise socket.error

      port   = struct.pack("!H", self.port)
      length = chr(len(self.host))

      self.send_ok = 1
      self.send(("\x05\x01\x00\x03%s%s%s" % (length, self.host, port)))
      self.send_ok = 0

      self.negotiation += 1

    elif self.negotiation == 1:
      if data != "\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00":
        raise socket.error("Connection refused.")

      self.send_ok   = 1
      self.negotiation += 1
      self.connected = True

      if self.ssl:
        self._sock = ssl.wrap_socket(self._sock)

      self.flush_send_queue()

    return data

  def send(self, data):
    if self.send_ok:
      return self._sock.send(data)
    else:
      self.send_queue.append(data)

  def flush_send_queue(self):
    for msg in self.send_queue:
      self.send(msg)

    self.send_queue = []

  def close(self):
    self._sock.close()

  def fileno(self):
    return self._sock.fileno()
