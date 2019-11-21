# fbhoststb
Small tool to send Telegram notification about devices connecting/disconnecting to/from a FritzBox.

## installation
Remark: Examples show how I did it on my RaspberryPi 3
Remark#2: I assume you already using Telegram
* Create your telegram bot (google how to do it)
* Notice the token of your bot
* Communicate once to your bot so the bot gets the permission to communicate with you
* Install python-telegram-bot: sudo apt-get install python3-pip && sudo pip3 install python-telegram-bot
* Install fritzconnection: sudo apt-get install libxslt-dev && sudo pip3 install fritzconnection
* Write something to your bot and then start the getchatid.py: python3 getchatid.py <TokenOfYourBot>
* Notice your chatId
* Rename fbhoststb.cfg.template into fbhoststb.cfg
* Fill the FritzBox credentials, token and the chatId in the fbhoststb.cfg
* Start the fbhoststb: python3 fbhoststb.py
* The program shall send you all current hosts over the Telegram
* The subsequent starts will only send the changes
* If everithing works you can add the program to your crontab:  "* * * * * cd fbhoststb && python3 fbhoststb.py"

