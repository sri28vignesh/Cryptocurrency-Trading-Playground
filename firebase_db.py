from email.policy import default
from re import I
from turtle import update
import pyrebase
import datetime
import uuid
import access_crypto_data as cp
from tabulate import tabulate
from decouple import config

firebaseConfig = {
  "apiKey": config.db_apiKey(default=''),
  "authDomain": config.db_authDomain(default=''),
  "databaseURL": config.db_databaseURL(default=''),
  "projectId": config.db_projectID(default=''),
  "storageBucket": config.db_storageBucket(default=''),
  "messagingSenderId": config.db_messagingSenderId(default=''),
  "appId": config.db_appId(default = ''),
  "measurementId": config.db_measurementId(default='')
}

firebase = pyrebase.initialize_app(firebaseConfig)

auth = firebase.auth()
db = firebase.database()


def create_wallet():
    '''creates a wallet and returns a wallet ID'''
    wallet_id = str(uuid.uuid1())
    try:
        db.child("wallets").child(wallet_id).set({"balance":50000})
    except:
        return False

    return wallet_id 

def create_user(uid, uname):
    if db.child("users").child(uid).get().val() != None:
        return "Exists"
    
    user_name = uname
    wallet_id = create_wallet()
    if wallet_id:
        user_data = {"user_name" : user_name, "wallet_id" : wallet_id }

        db.child("users").child(uid).set(user_data)
        return True
    else:
        return False

def get_wallet_balance(userid):
    '''retrieves the wallet balance of the user'''
    user_data = db.child("users").child(userid).get().val()
    return  db.child("wallets").child(user_data["wallet_id"]).child("balance").get().val()

def get_user_watchlist(userid):
    try:
        return db.child("watchlist").child(userid).get().val()
    except:
        return False


def add_user_watchlist(userid, coin_names):
    try:
        watch_list = get_user_watchlist(userid)
        if watch_list in (None,False):
            db.child("watchlist").child(userid).set(coin_names)
        else:
            db.child("watchlist").child(userid).set(   list(set(watch_list + coin_names))  )
        
        return True
    except:
        return False

def generate_trade_id(userid):
    trades = db.child("trades").order_by_child('userid').equal_to(userid).get().val()
    id = len(trades)
    # print(id)

    return f"{userid}-{id+1}"

def close_trade(tradeid):
    trade_data = db.child("trades").child(tradeid).get().val()
    coin_name = trade_data["opendata"]["name"]
    cur_price = cp.get_coin_price(coin_name)
    close_time = str(datetime.datetime.now())
    profit_percent = calc_profit(cur_price, trade_data["opendata"]["unit_price"])
    sell_amt = trade_data["opendata"]["units"] * float(cur_price) 

    trade_data["closetime"] = close_time
    trade_data["status"] = "closed"
    trade_data["profit_loss"] = profit_percent
    trade_data["closedata"] = {"name" : coin_name, 
                "unit_price": cur_price,
                "units": trade_data["opendata"]["units"],
                "sell_amt": sell_amt }
    
    try:
        db.child("trades").child(tradeid).set(trade_data)
        update_wallet(trade_data["userid"], sell_amt)
        return disp_close_trade(trade_data)
    except:
        return False


def disp_close_trade(trade_data):
    result = f'''*
             Name: {trade_data["closedata"]["name"]}
             Sold Units: {format(trade_data["closedata"]["units"], ".3f")}
             Total bought Amount: {format(trade_data["opendata"]["buy_amt"],".3f")}
             Total sold Amount: {format(trade_data["closedata"]["sell_amt"],".3f")}   
             Profit(%): {format(trade_data["profit_loss"],".3f")} 
    *'''
    return result


# def calc_sell_price(profit_percent, buy_price):
#     profit = (profit_percent/buy_price) * 100
#     return buy_price + profit


def open_trade(userid, symbol, amt):
    coin_dict = cp.get_symbol_and_names()
    coin_name = coin_dict[symbol]
    coin_info = cp.get_coin_info(coin_name)
    trade_id  = generate_trade_id(userid)
    units = float(amt) / float(coin_info["market_data"]["price_usd"]) 
    # print(units)
    
    open_data = {"name" : coin_info["name"], 
                "unit_price": coin_info["market_data"]["price_usd"],
                "units": units,
                "buy_amt": amt }
    open_time = str(datetime.datetime.now())
    trade_data = {"tradeid":trade_id, "userid":userid, "opentime":open_time, 
                 "opendata": open_data, "closetime":"" ,
                 "closedata":"", "status":"opened", "profit_loss":""
    }

    try:
        db.child("trades").child(trade_id).set(trade_data)
        print( update_wallet(userid, -amt) )
        return True
    except:
        return False

def calc_profit(sell_price, buy_price):
    profit = sell_price - buy_price
    return ( profit / buy_price ) * 100

def get_opened_trades(userid):
    try:
        trades = db.child("trades").order_by_child('userid').equal_to(userid).get().val()
        opened_trades = []
        for i, trade in enumerate(trades.values()):
            if trade["status"] == "opened":
                cur_price = cp.get_coin_price(trade["opendata"]["name"])
                trade["opendata"]["profit"] = calc_profit(cur_price, trade["opendata"]["unit_price"])

                opened_trades.append( [ i+1, trade["opendata"]["name"],
                                        trade["opendata"]["units"], trade["opendata"]["unit_price"],   
                                        trade["opendata"]["profit"] ])

        opened_trades = tabulate(opened_trades, floatfmt=".3f",headers=["Trade No.", "Coin Name", "Units bought", "Bought Unit Price(USD)", "Profit(%)"])


        return f'```{opened_trades}```'
    except:
        return False

def get_closed_trades(userid):
    try:
        trades = db.child("trades").order_by_child('userid').equal_to(userid).get().val()
        closed_trades = []
        for i, trade in enumerate(trades.values()):
            if trade["status"] == "closed":
                # cur_price = cp.get_coin_price(trade["closedata"]["name"])
                # trade["closedata"]["profit"] = calc_profit(cur_price, trade["opendata"]["unit_price"])

                closed_trades.append( [ i+1, trade["closedata"]["name"],
                                        trade["closedata"]["units"], trade["closedata"]["unit_price"],   
                                        trade["closedata"]["sell_amt"] ])

        closed_trades = tabulate(closed_trades, floatfmt=".3f",headers=["Trade No.", "Coin Name", "Units Sold", "Sold Unit Price(USD)", "Sold Amount(USD)"])


        return f'```{closed_trades}```'
    except:
        return False


def get_all_trades(userid):
    opened = get_opened_trades(userid)
    closed = get_closed_trades(userid)

    result = "\n\n*List of opened trades*\n\n" + opened + "\n\n*List of closed trades*\n\n" + closed
    return result

def update_wallet(userid,amt):
    try:
        wallet_id = db.child("users").child(userid).child("wallet_id").get().val()
        balance = db.child("wallets").child(wallet_id).child("balance").get().val()
        db.child("wallets").child(wallet_id).child("balance").set(balance+amt)
        return True
    except:
        return False

if __name__ == "__main__":
    uid = 800528877
    names = ['litecoin', 'cosmos']
    # print(get_wallet_balance(uid))
    # print(add_user_watchlist(uid,names))
    # print(get_user_watchlist(uid))
    # print(generate_trade_id(uid) )
    # num = 50
    # print(update_wallet(uid, -num))
    print(get_opened_trades(uid))
