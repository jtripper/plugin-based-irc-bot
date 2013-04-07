#!/bin/bash

for file in $(ls plugins/*.py)
do
  sed -i 's/self, bot/self/g' $file
  sed -i 's/self\.bot = bot//g' $file 
  sed -i 's/self.bot/sock/g' $file
  sed -i 's/self, buffer/self, bot, sock, buffer/g' $file
  sed -i 's/self, auth_level, buffer/self, bot, sock, auth_level, buffer/g' $file
done

