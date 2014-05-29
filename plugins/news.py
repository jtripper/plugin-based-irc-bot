# news.py
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

from urllib2 import urlopen
import feedparser
import tinyurl

class news:
    def __init__(self):
        self.printed = []
        self.feeds = {
          'cnn':'http://rss.cnn.com/rss/cnn_latest.rss',
          'cnet':'http://feeds.feedburner.com/cnet/tcoc.rss',
          'reuters_us':'http://feeds.reuters.com/Reuters/domesticNews.rss',
          'reuters_tech':'http://feeds.reuters.com/reuters/technologyNews.rss',
          'reuters_world':'http://feeds.reuters.com/Reuters/worldNews.rss',
          'nyt_tech':'http://rss.nytimes.com/services/xml/rss/nyt/Technology.xml',
          'nyt_world':'http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
          'forbes':'http://www.forbes.com/real-time/feed2/',
          'forbes_tech':'http://www.forbes.com/technology/feed/'
        }

        self.allowed_functions = {
          'help':0,
          'list':0
        }

        for feed in self.feeds:
          self.allowed_functions[feed] = 0
          self.__dict__[feed] = self.get_five

    def help(self, bot, sock, buffer):
        sock.msg(buffer.to, "Usage: ")
        sock.msg(buffer.to, " * news.cnn -- change cnn to your favorite news site")
        sock.msg(buffer.to, " * news.cnn more -- to load more news")
        
    def list(self, bot, sock, buffer):
        sock.msg(buffer.to, "\x0300Available news sources:")
        for feed in self.feeds:
            sock.msg(buffer.to, " * %s " % (feed))

    def get_five(self, bot, sock, buffer):
        rss = buffer.msg.split()[0].split(".")[1]
        d = feedparser.parse(self.feeds[rss])

        more = buffer.msg.split()
        if len(more) > 1 and more[1] == "more":
            more = True
        else:
            more = False

        num = 0
        for e in d.entries:
            if e.link not in self.printed or not more:
                url = tinyurl.create_one(e.link)
                if e.link not in self.printed: self.printed.append(e.link)
                sock.msg(buffer.to, '\x0304%s\x03 \x0300-- Read more: %s' % (e.title, url))
                num += 1
                if num == 5: break
