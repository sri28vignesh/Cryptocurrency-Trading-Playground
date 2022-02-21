import telebot

TOKEN = open("secret-token").read()
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome!, How are you doing?")

@bot.message_handler( func = lambda message:True)
def echo_all(message):
    bot.reply_to(message, message.text )

if __name__ == "__main__":
    bot.infinity_polling()
