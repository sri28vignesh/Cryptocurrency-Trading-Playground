from email import message
from flask import Flask,request,jsonify
from crypto_trading_bot import bot

app = Flask(__name__)

@app.route("/")
def test_msg():
    bot.infinity_polling()
    return jsonify(message="Bot Service Stoped!")




if __name__ == "__main__":
    app.run(debug=True)