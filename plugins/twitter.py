# twitter.py
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

import tweepy
import re
import HTMLParser

class twitter:
  def __init__(self, bot):
    self.allowed_functions = { 'tweet':1, 'follow':2, 'reply':1, 'retweet':1, 'delete':2, 'help':1 }

    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    self.api = tweepy.API(auth)
    self.bot = bot

  def tweet(self, buffer):
    text       = ' '.join(buffer.msg.split()[1:])

    if len(text) < 140:
      tweet = self.api.update_status(text)
      self.bot.msg(buffer.to, "Tweet URL: https://twitter.com/%s/status/%s" % (tweet.author.screen_name, tweet.id))

    else:
      split_msg = list(re.findall(".?"*110, text))
      length = len(split_msg)
      tweet = None

      if split_msg[-1] == "":
        length -= 1

      if length > 5:
        self.bot.msg(buffer.to, "%d messages.... really?! Asshole." % length)
        return

      for i, msg in enumerate(split_msg):
        if msg == "":
          continue
        if tweet != None:
          tweet = self.api.update_status("%d/%d ...%s -- @%s" % (i + 1, length, msg, tweet.author.screen_name), tweet.id)
        else:
          try:
            tweet = self.api.update_status("%d/%d %s" % (i + 1, length, msg))
          except Exception as e:
            self.bot.msg(buffer.to, buff.to, "%s" % e)
          self.bot.msg(buffer.to, "Tweet URL: https://twitter.com/%s/status/%s" % (tweet.author.screen_name, tweet.id))

  def follow(self, buffer):
    username   = buffer.msg.split()[1] 

    try:
      self.api.create_friendship(username)
      self.bot.msg(buffer.to, "Followed %s" % username)
    except Exception as e:
      self.bot.msg(buffer.to, "Error: %s" % str(e))

  def reply(self, buffer):
    url        = buffer.msg.split()[1]
    tweet      = ' '.join(buffer.msg.split()[2:])

    (author, tweet_id) = re.search("https?://w?w?w?\.?twitter.com/([^/]+)/statuse?s?/([^ ]+)", url).groups()
    if user not in tweet:
      tweet = user + ' ' + tweet
    tweet = self.api.update_status(tweet, tweet_id)
    self.bot.msg(buffer.to, "Tweet URL: https://twitter.com/%s/status/%s" % (tweet.author.screen_name, tweet.id))

  def retweet(self, buffer):
    tweet_id = re.search("https?://w?w?w?\.?twitter.com/.*/statuse?s?/([^ ]+)", buffer.msg).group(1)
    self.api.retweet(tweet_id)
    h = HTMLParser.HTMLParser()
    tweet = self.api.get_status(id=tweet_id)
    tweet.text = h.unescape(tweet.text)
    self.bot.msg(buffer.to, "Retweeted: <%s> %s -- %s" % (tweet.author.screen_name, tweet.text, "https://twitter.com/%s/status/%s" % (tweet.author.screen_name, tweet.id)))

  def delete(self, buffer):
    tweet_id = re.search("https?://w?w?w?\.?twitter.com/.*/statuse?s?/([^ ]+)", buffer.msg).group(1)
    tweet = self.api.destroy_status(id=tweet_id)
    self.bot.msg(buffer.to, "Deleted: %s" % ("https://twitter.com/%s/status/%s" % (tweet.author.screen_name, tweet.id)))

  def help(self, buffer):
    self.bot.msg(buffer.to, "Usage:")
    self.bot.msg(buffer.to, "  twitter.tweet   <tweet>")
    self.bot.msg(buffer.to, "  twitter.retweet <url>")
    self.bot.msg(buffer.to, "  twitter.delete  <url>")
    self.bot.msg(buffer.to, "  twitter.reply   <url>   <tweet>")
    self.bot.msg(buffer.to, "  twitter.follow  <user>")
