from click import command
import telebot
from telebot import types, util
import firebase_db as fdb 
import access_crypto_data as cp
from tabulate import tabulate
from decouple import config

TOKEN = config.telebot_api_key(default='')
bot = telebot.TeleBot(TOKEN)
watchlist_one, watchlist_two = None, None

cmd_template = '''
    <b>Welcome to the crypto trading playground!</b>

You're given with initial $50000 virtual wallet money and 
you can play and trade with the available cryptocurrencies.

Here are the list of commands to access the playground:
 Command                  Description
/available_cryptos  ->   Provides the list of available cryptocoins
/wallet_balance     ->   Displays the available wallet balance
/watchlist          ->   Provides info of watchlisted coins
/add_watchlist      ->   Helps to create and add coins to watchlist
/open_trade         ->   Initiates a trade on selected coin
/close_trade        ->   Stops a trade on selected coin
/myassets           ->   Provides the list of current holdings
/mytrades           ->   Provides current and closed trade information

'''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message ):
    '''sends welcome message to user when /start or /help command is used.'''
    bot.reply_to(message, f"Welcome {message.chat.first_name}!, How are you doing?" )
    bot.send_message(message.chat.id, cmd_template, parse_mode = "HTML" )
    if(fdb.create_user(message.chat.id, message.chat.first_name)):
        print("User Created in Firebase DB.")
    else:
        print("There is a problem in creating user!")


@bot.message_handler(commands=['wallet_balance'] )
def send_wallet_balance(message):
    '''sends the wallet balance of the user'''
    balance = fdb.get_wallet_balance(message.chat.id)
    print(balance)
    bot.reply_to(message, f"* Your Wallet balance is : ${balance} *", parse_mode = "Markdown")

@bot.message_handler(commands=['available_cryptos'])
def send_available_cryptos(message):
    """sends the list of available cryptocurrencies to the user chat"""
    bot.reply_to(message, cp.get_crypto_list(), parse_mode = "Markdown")  

@bot.message_handler(commands=["add_watchlist"])
def add_to_watchlist(message):
    '''receives a list of cryptos and adds to watchlist for the user'''
    global watchlist_one, watchlist_two
    user_id = message.chat.id
    coin_names = cp.get_crypto_names()
    watchlist_one = bot.send_poll(user_id, question="Select the cryptocurrencies to add to your watchlist -Part 1", options= coin_names[:10], is_anonymous=False, allows_multiple_answers=True)
    watchlist_two = bot.send_poll(user_id, question="Select the cryptocurrencies to add to your watchlist -Part 2", options= coin_names[10:], is_anonymous=False, allows_multiple_answers=True)    
    # print(len(coin_names), watchlist_one.poll.id, watchlist_two.poll.id) 

@bot.poll_answer_handler(func = lambda response:True)
def receive_watchlist(response):
    '''receives a list of cryptos from user's poll and adds to the user's watchlist'''
    coin_names = cp.get_crypto_names()
    coin_names_one, coin_names_two = coin_names[:10], coin_names[10:]
    # print(response.user) 
    if response.poll_id == watchlist_one.poll.id:
        # print(coin_names_one, response.user.id, response.option_ids)
        coin_names = pack_watchlist_names(coin_names_one, response.option_ids)
        fdb.add_user_watchlist(response.user.id, coin_names)
    else:
        # print(coin_names_two, response.user.id, response.option_ids)
        coin_names = pack_watchlist_names(coin_names_two, response.option_ids)
        fdb.add_user_watchlist(response.user.id, coin_names)
    # print(response.__dict__)

def pack_watchlist_names(names, indices):
    return [names[i] for i in indices]


@bot.message_handler(commands=['watchlist'])
def send_watchlist(message):
    '''sends the watchlisted cryptocurrency metrics to the user chat'''
    user_id = message.chat.id
    watchlist = cp.get_watchlist_info(user_id)
    bot.reply_to(message, watchlist, parse_mode = "Markdown")


@bot.message_handler(commands=['open_trade'])
def disp_trade_coins(message):
    '''sends the list of coins to open a trade'''
    coin_names = "\n".join( [ f' {i+1}. {name}' for i,name in enumerate(cp.get_crypto_names()) ] )
    coin_names = "\t *Choose any coin to open a trade or buy:*\n\n" + coin_names +"\n\n Enter ot{number} to select a coin, Eg: ot1 ->selects bitcoin."
    bot.reply_to(message, coin_names, parse_mode = "Markdown")

@bot.message_handler(regexp="^ot-(.)+-buy-(.)+")
def get_opentrade_amt(message):
    '''receives the amount and coin from the user to open a trade, format-> ot-BTC-buy-100 '''
    trade_data = message.text.split("-")
    userid = message.chat.id
    _,symbol,_,amt = trade_data 
    print( fdb.open_trade(userid, symbol, float(amt) ) )    
    bot.reply_to(message, f"You have opened a buying trade of {symbol} for amount: ${amt} \n\n Please use /myassets command to view your holdings.")


@bot.message_handler(commands=['close_trade'])
def disp_opened_trades(message):
    '''sends the list of opened trade by the user to close'''
    trades = fdb.get_opened_trades(message.chat.id)   
    result = '''* Close a Trade ----- Select any opened trade listed below *\n\n'''
    result = result + trades + '''\n
    Enter *ct\"number\"* to close a particular trade\n
    Eg: ct1 -> closes the trade number 1''' 
    
    if trades == "":
        result = "Sorry, there is no trade to close!"
    bot.reply_to(message, result, parse_mode = "Markdown")

@bot.message_handler(regexp="^ct([1-9]|1[0-9]?|20)$")
def get_closetrade_id(message):
    '''receives trade id from user and closes the trade by selling the coin'''
    userid = message.chat.id
    trade_id = str(userid) +"-"+ message.text[2:]
    result = fdb.close_trade(trade_id)   
    bot.reply_to(message, "You have closed your selected trade!\n"+result, parse_mode = "Markdown")

@bot.message_handler(regexp="^ot([1-9]|1[0-9]?|20)$" )
def get_opentrade_coin(message):
    '''receives coin to open a trade and messages which matches numbers between 1 and 20'''
    coin_names = cp.get_crypto_names()
    coin_num = int(message.text[2:])
    result = cp.get_crypto_metrics(coin_names[coin_num-1])
    bot.reply_to(message, result, parse_mode = "Markdown" )

@bot.message_handler(commands=["myassets"])
def send_myassets(message):
    '''sends the current cryptocurrency holdings of the user'''
    userid = message.chat.id
    trades = fdb.get_opened_trades(userid)
    result = "    *MyAssets ----- List of current crypto holdings*   \n\n"
    result += trades

    if trades == [] or trades == False:
        result = "Sorry, there is no assets to show!"
    bot.reply_to(message, result, parse_mode = "Markdown" )

@bot.message_handler(commands=['mytrades'])
def send_mytrades(message):
    '''sends the both opened and closed trades by the user'''
    userid = message.chat.id
    trades = fdb.get_all_trades(userid)
    result = "     *MyTrades ----- List of Crypto Trades*     \n"
    result += trades

    if trades == [] or trades == False:
        result = "Sorry, there is no trades to show!"
    bot.reply_to(message, result, parse_mode = "Markdown" )


@bot.message_handler( func = lambda message:True )
def echo_all(message):
    '''Sends back the received message from user'''
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, parse_mode="Markdown", text= "*Sorry I could n't recognise this command, I'm still learning.*" , reply_markup=markup)






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
