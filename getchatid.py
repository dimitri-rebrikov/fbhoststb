from telegram import Bot
import sys
token=sys.argv[1]
bot = Bot(token=token)
updates = bot.get_updates()
print([u.message.text for u in updates])
chatId = bot.get_updates()[-1].message.chat_id
print ("YourChatID: {}".format(chatId))