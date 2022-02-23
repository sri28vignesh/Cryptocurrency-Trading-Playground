from click import command
import telebot
from telebot import types, util
import firebase_db as fdb 
import access_crypto_data as cp

TOKEN = open("secret-token").read()
bot = telebot.TeleBot(TOKEN)
watchlist_one, watchlist_two = None, None

cmd_template = f'''
    **Welcome to the crypto trading playground!**

You're given with initial $50000 virtual wallet money and 
you can play and trade with the available cryptocurrencies.

Here are the list of commands to access the playground:
 Command                  Description
/available_cryptos  ->   Provides the list of available cryptocoins
/wallet_balance     ->   Displays the available wallet balance
/watchlist          ->   Provides info of watchlisted coins
/add_watchlist      ->   Helps to create and add coins to watchlist
/myassets           ->   Provides the list of current holdings
/open_trade         ->   Initiates a trade on selected coin
/close_trade        ->   Stops a trade on selected coin
/mytrades           ->   Provides current and closed trade information

'''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message ):
    '''sends welcome message to user when /start or /help command is used.'''
    bot.reply_to(message, f"Welcome {message.chat.first_name}!, How are you doing?" )
    bot.send_message(message.chat.id, cmd_template )
    if(fdb.create_user(message.chat.id, message.chat.first_name)):
        print("User Created in Firebase DB.")
    else:
        print("There is a problem in creating user!")


@bot.message_handler(commands=['wallet_balance'] )
def send_wallet_balance(message):
    '''sends the wallet balance of the user'''
    balance = fdb.get_wallet_balance(message.chat.id)
    print(balance)
    bot.reply_to(message, f"Your Wallet balance is : ${balance}")

@bot.message_handler(commands=['available_cryptos'])
def send_available_cryptos(message):
    """sends the list of available cryptocurrencies to the user chat"""
    bot.reply_to(message, cp.get_crypto_list())  

@bot.message_handler(commands=["add_watchlist"])
def add_to_watchlist(message):
    '''receives a list of cryptos and adds to watchlist for the user'''
    user_id = message.chat.id
    coin_names = cp.get_crypto_names()
    watchlist_one = bot.send_poll(user_id, question="Select the cryptocurrencies to add to your watchlist -Part 1", options= coin_names[:10], is_anonymous=False, allows_multiple_answers=True)
    watchlist_two = bot.send_poll(user_id, question="Select the cryptocurrencies to add to your watchlist -Part 2", options= coin_names[10:], is_anonymous=False, allows_multiple_answers=True)    
    # print(len(coin_names), watchlist_one.poll.id, watchlist_two.poll.id) 

@bot.poll_answer_handler(func = lambda response:True)
def receive_watchlist(response):
    coin_names = cp.get_crypto_names()
    coin_names_one, coin_names_two = coin_names[:10], coin_names[10:] 
    if response.poll_id == watchlist_one.poll.id:
        print(coin_names_one, response.user.chat.id, response.option_ids)
    else:
        print(coin_names_two, response.user.chat.id, response.option_ids)
    # print(response.__dict__)


@bot.message_handler(commands=['watchlist'])
def send_watchlist(message):
    '''sends the watchlisted cryptocurrency metrics to the user chat'''
    user_id = message.chat.id
    watchlist = cp.get_watchlist_info(user_id)
    bot.reply_to(message, watchlist)


@bot.message_handler( func = lambda message:True )
def echo_all(message):
    '''Sends back the received message from user'''
    bot.send_message(message.chat.id, message.text )





#chat_member_handler. When status changes, telegram gives update. check status from old_chat_member and new_chat_member.
@bot.chat_member_handler()
def chat_m(message: types.ChatMemberUpdated):
    old = message.old_chat_member
    new = message.new_chat_member
    if new.status == "member":
        bot.send_message(message.chat.id,"Hello {name}!".format(name=new.user.first_name)) # Welcome message
        print(new.user.id)

if __name__ == "__main__":
    bot.infinity_polling(allowed_updates=util.update_types)
