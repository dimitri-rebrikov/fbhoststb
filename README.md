# fbhoststb
Small tool to send Telegram notification about devices connecting/disconnecting to/from a FritzBox

## installation
Insall python-telegram-bot and fritzconnection (using pip)
Create a telegram bot (see corresponding documentation at telegrams website)
Rename fbhoststb.cfg.template into fbhoststb.cfg and fill the (missing) config data

## start
python fbhoststb.py

during the first start the script will notify about all hosts
during the nexts start the script will notify only about changes 
the idea is to run the script automatically on the regular basis, 
for example using crontab:
* * * * * python fbhoststb.py
