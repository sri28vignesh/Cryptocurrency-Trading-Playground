from email.mime import base
import requests
import firebase_db as fdb

header_data = {"x-messari-api-key" : "1945b43f-0adb-485d-b9bc-2c294871e0bb"}
base_url = "https://data.messari.io/api/v1/assets?"

def get_crypto_list():
    '''fetches cryptocurrency data from messari api and returns list of coins with their metrics'''

    param = {"fields" : "id,slug,symbol,metrics/market_data/price_usd,metrics/market_data/percent_change_usd_last_24_hours"}
    res = requests.get(base_url, params=param , headers=header_data)
    crypto_data = res.json()
    crypto_list = "\n".join( [ f' {coin["slug"]}\t\t {coin["symbol"] }\t\t  {coin["metrics"]["market_data"]["price_usd"]}\t\t  {coin["metrics"]["market_data"]["percent_change_usd_last_24_hours"]}'  for coin in crypto_data["data"] ] )
    result = "**Available list of cryptocurrencies** \n\n Name \t\t      Symbol \t\t      Price(USD) \t\t    Last 24 Hrs Change(%)\n" + crypto_list
    return result

def get_crypto_names():
    crypto_data = requests.get(base_url, params={"fields": "id,slug,symbol,metrics/market_data/price_usd"}, headers= header_data).json()
    return [ coin["slug"] for coin in crypto_data["data"] ]

def get_crypto_metrics(name):
    coin = requests.get(base_url[:-1]+f'/{name}/metrics', headers=header_data ).json()["data"]
    result = f'''** Open a Trade ---- Selected Cryptocurrency **\n\n
                Name:  {name}\n
                Symbol: {coin["symbol"]}\n
                Price(USD): {coin["market_data"]["price_usd"]}\n
                Last 24 Hrs Change(%): {coin["market_data"]["percent_change_usd_last_24_hours"]}\n\n
                Please note: Min buy price is $100\n\n
    Enter `ot-{coin['symbol']}-buy-priceamt` to open a trade on {name}\n
    Eg: ot-{coin['symbol']}-buy-100
              '''
    return result

def get_coin_info(name):
    return requests.get(base_url[:-1]+f'/{name}/metrics', headers=header_data ).json()["data"]

def get_coin_price(name):
    return requests.get(f"https://data.messari.io/api/v1/assets/{name}/metrics", headers=header_data ).json()["data"]["market_data"]["price_usd"]

def get_symbol_and_names():
    crypto_data = requests.get(base_url, params={"fields": "id,slug,symbol,metrics/market_data/price_usd"}, headers= header_data).json()["data"]
    return { coin["symbol"]:coin["slug"] for coin in crypto_data }

def get_watchlist_info(uid):
    coin_names = fdb.get_user_watchlist(uid)
    watchlist = ""
    if coin_names:
        for name in coin_names:
            coin = requests.get( base_url[:-1]+f'/{name}/metrics', headers=header_data ).json()["data"]
            watchlist += f' {coin["slug"]}\t\t {coin["symbol"] }\t\t  {coin["market_data"]["price_usd"]}\t\t  {coin["market_data"]["percent_change_usd_last_24_hours"]}\n'
        result = "**Your Watchlist of cryptocurrencies** \n\n Name \t\t      Symbol \t\t      Price(USD) \t\t    Last 24 Hrs Change(%)\n" + watchlist
        return result
    else:
        return "Watchlist is empty!"

if __name__ == "__main__":
    uid = 800528877
    # print(get_watchlist_info(uid))
    # print(get_crypto_names())
    # print(get_crypto_list())
    print( get_symbol_and_names() )