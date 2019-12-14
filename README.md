# fbhoststb
Small tool to send Telegram notification about devices connecting/disconnecting to/from a FritzBox.

## installation
Remark: Examples show how I did it on my RaspberryPi 3

Remark#2: I assume you are already using Telegram

* Create your telegram bot (google how to do it)
* Notice the token of your bot
* Communicate once with your bot so the bot gets the permission to communicate with you
* Install python3 if not already installed
* Install python3's pip: sudo apt-get install python3-pip
* Install python3's lxml library: sudo apt-get install python3-lxml
* If your distribution does not have python3-lxml package you might try to install it over pip: sudo apt-get install libxslt-dev && sudo pip3 install lxml
* Install python-telegram-bot: sudo pip3 install python-telegram-bot
* Install fritzconnection: sudo pip3 install fritzconnection
* Write something to your bot and then start the getchatid.py: python3 getchatid.py \<TokenOfYourBot\>
* Notice your chatId
* Rename fbhoststb.cfg.template into fbhoststb.cfg
* Fill the FritzBox credentials, token and the chatId in the fbhoststb.cfg
* Start the fbhoststb: python3 fbhoststb.py
* The program will first send you all current hosts over the Telegram
* After that the programm will check for changes ever 30th second and send only the changes
* To stop the program use Ctrl+C or "kill"
* To start the program during each boot you might use the special crontab "@reboot" function:  "@reboot sleep 30 && cd fbhoststb && python3 fbhoststb.py >> fbhoststb.log 2>&1 &"

