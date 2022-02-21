import telebot

TOKEN = "5112747288:AAFbhd8HWD2xzIKHY1lAECoCEw0_Tv96cq0"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome!, How are you doing?")

@bot.message_handler( func = lambda message:True)
def echo_all(message):
    bot.reply_to(message, message.text )

if __name__ == "__main__":
    bot.infinity_polling()
