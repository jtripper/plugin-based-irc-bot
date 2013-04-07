for file in $(ls plugins/*.py)
do
  sed -i \'s/self, bot/self/g\' plugins/$file
  sed -i \'s/self\.bot = bot//g\' plugins/$file 
  sed -i \'s/self.bot/sock/g\' plugins/$file
  sed -i \'s/self, buffer/self, bot, sock, buffer/g\' plugins/$file
  sed -i \'s/self, auth_level, buffer/self, bot, sock, auth_level, buffer/g\' plugins/$file
done
