class control:
  def __init__(self, bot):
    self.allowed_functions = { 'quit':10 }
    self.bot = bot

  def quit(self, buffer):
    self.bot.disconnect()
