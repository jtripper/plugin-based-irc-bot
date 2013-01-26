# Plugin-based IRC Bot

This is an IRC bot that uses plugins for everything. Plugins can be reloaded, unloaded, and loaded at run time and are very simple to write.

## Configuration

To configure, open main.py and set the necessary settings at the beginning of the file. 

```python
# irc network, port, nickname, username, real name, and ssl on
bot = IRC("irc.com", 6697, "Dat_Bot", "testing", "testing", use_ssl=1)
# set bot to +B
bot.raw("MODE Dat_Bot +B")
# channel
bot.join("#test1")

....

authentication = auth(bot)
# change this to your nick
authentication.auth_levels[''] = 10

```

After this is configured, the bot can be started.

## Usage

Note that the bot does not have to be registered, but the bot master does. The bot requires that all users bet registered and logged in. If necessary, this could be changed.

General usage for the plugins is:

```
plugin_name.command <arguments>
```

So, to tweet using the twitter plugin the syntax would be:

```
twitter.tweet My first tweet!
```

In order to use the twitter plugin, keys need to be set inside twitter.py. 

To add more users to the bot, use the auth.level command:

```
auth.level [user] [level]
```

Authentication levels are arbitrary, however every command has a required authentication level that a user must meet or exceed to execute the command.

## Plugin Writing Guide

An example of plugin writing is in plugins/hello_world.py.disabled but will be detailed more here. Every plugin must contain one class and the class name must be the same as the file name. The class name will be used to call the plugin, so twitter.py has the twitter class which is called with twitter by the user.

Inside the class's __init__ function there should be a dictionary called self.authorized_functions. This dictionary should contain function_name:auth_level. The function_name is a string containing a permitted function, tweet for example. auth_level is the minimum authentication level required to execute the function.

Another important variable is self.autorun. This is a function that is executed every time a message is received, regardless of message type and whether or not the user executed a command.

Every class should also have a help() function that lists the command usage, this is automatically executed upon errors. 

The __init__ function should accept the IRC class as an argument and save this as self.bot. Every other function should accept an instance of the Message class. 

### IRC()

The IRC class is what handles the bulk of the bot, functions of interest maybe the join(), nick(), msg(), ctcp(), and notice() functions. See the supplied plugins for examples of these.

### Message()

The Message class is what all of the buffers come in as, it has several useful variables. It comes with the to, chan, sender, type, and msg variables.

* to contains the nickname / channel name of who to reply to if a message is going to be sent, for example in a channel message the channel name is stored, in a private message the sender's name is stored.
* chan contains the channel that the message was sent to or None if it is a private message.
* sender contains the sender of the message.
* type stores the type of message, PRIVMSG, NOTICE, NICK, KICK, etc.
* msg stores the message that is contained.
