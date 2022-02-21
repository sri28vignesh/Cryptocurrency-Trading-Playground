from email import message
from flask import Flask,request,jsonify
from crypto_trading_bot import bot
# TOKEN = "5112747288:AAFbhd8HWD2xzIKHY1lAECoCEw0_Tv96cq0"
app = Flask(__name__)

@app.route("/")
def test_msg():
    bot.infinity_polling()
    return jsonify(message="Bot Service Stoped!")




if __name__ == "__main__":
    app.run(debug=True)