import requests

def get_crypto_list():
    res = requests.get("https://data.messari.io/api/v1/assets?")
    crypto_data = res.json()
    crypto_list = "\n".join( [ f' {coin["name"]}\t\t {coin["symbol"] }\t\t  {coin["metrics"]["market_data"]["price_usd"]}\t\t  {coin["metrics"]["market_data"]["percent_change_usd_last_24_hours"]}'  for coin in crypto_data["data"] ] )
    result = "**Available list of cryptocurrencies** \n\nName       Symbol       Price(USD)     Last 24 Hrs Change(%)\n" + crypto_list
    return result

if __name__ == "__main__":
    get_crypto_list()