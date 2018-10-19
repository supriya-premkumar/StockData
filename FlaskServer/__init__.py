from flask import Flask, request
import json
import pymongo
import sys

app = Flask(__name__)

client = pymongo.MongoClient('localhost', 27017)
db = client['stock_data']
posts = db.posts

stockPrice = []


def compute_max_profit(hd):
    """
    stockProfit: returns maximum profit yielded by single buy and sell date
                 over the last 180 days
    :param hd: historical data, List
    :return: maxProfit, float
    """
    print("Compute MAx PRofit", hd)
    min_value = sys.maxsize
    max_profit = 0
    buy_sell = dict()
    buy_idx = 0
    best_buy_price = 0
    best_sell_price = 0
    best_buy_date = ""
    best_sell_date = ""
    i = 0
    while i < len(hd):
        price = float(hd[i]['price'])
        if price < min_value:
            min_value = price
            buy_idx = i

        diff = price - min_value
        if diff > max_profit:
            max_profit = diff
            best_buy_date = hd[buy_idx]['date']
            best_buy_price = hd[buy_idx]['price']
            best_sell_date = hd[i]['date']
            best_sell_price = price
        i += 1
    buy_sell['buy'] = best_buy_date
    buy_sell['sell'] = best_sell_date
    buy_sell['best_buy_price'] = best_buy_price
    buy_sell['best_sell_price'] = best_sell_price
    buy_sell['max_profit'] = max_profit
    return buy_sell


def retrieve_data(sym):
    """
    retrieveData: Retrieves the data from the mongoDB based on the given parameter
                  sends the retrieved symbol as parameter to the stockProfit function
    :param sym: stock symbol, string
    :return: void
    """
    row = posts.find_one({"_id": sym})
    return row[sym]


@app.route('/', methods=['POST'])
def query_example():
    query = request.get_json()
    print(query["stock"])
    historic_prices = retrieve_data(query["stock"])
    print(len(historic_prices))
    print(historic_prices)
    max_profit = compute_max_profit(historic_prices)
    print(max_profit)
    return json.dumps(max_profit)


if __name__ == '__main__':
    app.run('localhost', port=8080)
