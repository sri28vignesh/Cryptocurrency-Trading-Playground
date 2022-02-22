# Cryptocurrency-Trading-Playground
A Telegram Bot provides a virtual playground to explore and do some mock trading.

`Features and Use cases`
- User management -> Handling single user and groups
- Listing Available Coins -> List of available coins along with their properties and description such as current price, open-price, close-price, 24Hrs Change, and etc
- Selective Currency Inspection
- Creating favourite / watchlist
- Perform Mock Trading -> Involves buying and selling multiple coins and can keep track on them.
- Inspect Trade Status -> Performing inspection on current and past trades and measured in profit & loss percentage.
- Listing My Assets -> List of purchased coins along with their attributes.

`Pulling data via API`
- https://api2.lunarcrush.com/v2
- https://developers.cryptoapis.io/technical-documentation/general-information/overview
- https://messari.io/api

`Tech Stack` -> Python + Telegram Bot API

`Hosting` -> Heroku

`Telegram Bot Link` ->  [Crypto-Trading-Playground](https://t.me/Crypto_trading_plaground_bot)

## Telegram Bot Commands

| **Commands**          | **Description**  |
| ------------------    | ---------------- |
| /available_cryptos    | Provides the list of available cryptocoins |
| /wallet_balance       | Displays the available wallet balance |
| /watchlist            | Provides info of watchlisted coins |
| /add_watchlist        | Helps to create and add coins to watchlist |
| /myassets             | Provides the list of current holdings |
| /open_trade           | Initiates a trade on selected coin |
| /close_trade          | Stops a trade on selected coin |
| /mytrades             | Provides current and closed trade information | 
