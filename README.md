# Bloonbot

Before bot can run, the following mods must be installed via [BTD6 Mod Manager](https://github.com/TDToolbox/BTD6-Mod-Manager):

* [BloonBot](https://github.com/jamesspalding/bloonbot/blob/main/BloonBot.cs)
* [Faster Forward](https://github.com/doombubbles/faster-forward)
* [Auto Nudge](https://github.com/doombubbles/auto-nudge)

server.py must be running while game is open, otherwise slowdown will occur when BloonBot attempts to retrieve data.


## Files

* bloon_bot.py contains all functions related to controlling the game

* bloon_brain.py contains all learning functions used to improve performance of the bot

* server.py starts the server to listen for information from BloonBot.cs

* main.py contains game logic and when to apply functions

