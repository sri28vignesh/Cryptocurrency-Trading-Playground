import pyrebase
import datetime
import uuid
import json

firebaseConfig = {
  "apiKey": "AIzaSyAAdaCTBZND0bGq4YUPFEiWtaWVkBDydVg",
  "authDomain": "crypto-trading-playground.firebaseapp.com",
  "databaseURL": "https://crypto-trading-playground-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "crypto-trading-playground",
  "storageBucket": "crypto-trading-playground.appspot.com",
  "messagingSenderId": "229453374449",
  "appId": "1:229453374449:web:eafb59479243306d56da50",
  "measurementId": "G-48XKP0LE1E"
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


if __name__ == "__main__":
    uid = 800528877
    names = ['litecoin', 'cosmos']
    # print(get_wallet_balance(uid))
    print(add_user_watchlist(uid,names))
    print(get_user_watchlist(uid))