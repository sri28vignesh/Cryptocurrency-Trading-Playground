from email import message
from flask import Flask,request,jsonify
from crypto_trading_bot import bot,util

app = Flask(__name__)

@app.route("/")
def test_msg():
    bot.infinity_polling(allowed_updates=util.update_types)
    return jsonify(message="Bot Service Stoped!")




if __name__ == "__main__":
    app.run(debug=True)