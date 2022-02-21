import requests

def get_crypto_list():
    res = requests.get("https://data.messari.io/api/v1/assets?")
    crypto_data = res.json()
    symbols = [cryp_data["symbol"] for cryp_data in crypto_data["data"]]
    print(symbols)

if __name__ == "__main__":
    get_crypto_list()