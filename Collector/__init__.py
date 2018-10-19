from alpha_vantage.timeseries import TimeSeries
from dateutil import parser
import datetime
import operator
from pymongo import MongoClient
import csv
import time

NUMBER_OF_DAYS = 180

client = MongoClient('localhost', 27017)
db = client['stock_data']
posts = db.posts


def is_in_range(t):
    """
    is_in_range: takes string parameter and converts it to datetime.
               Checks if the param datetime is in the given datetime range
               and returns a boolean
    :param t: string
    :return: bool
    """
    try:

        dt = parser.parse(t)
        now = parser.parse(datetime.datetime.today().strftime("%Y-%m-%d"))
        delta = datetime.timedelta(days=NUMBER_OF_DAYS)
        start_date = now - delta

        print(now)
        print(start_date)
        if start_date <= dt <= now:
            return True
        else:
            return False
    except ValueError as e:
        print("Could not parse date from string ", e)
        return False
    except TypeError as e:
        print("Invalid type ", e)
        return False


def fetch_historic_data(sym):
    """
    fetch_historic_data: fetches the historic stock information for a given ticker symbol
    and truncates the output size to last 180 days. The API doesn't accept an output size count
    :param sym: stock symbol, string
    :return: row which has a list of stock past 180 days stock price
    """
    ts = TimeSeries(key=' KWVML6RMN6II978O', indexing_type='date', output_format='json')
    try:
        data, meta_data = ts.get_daily(sym, outputsize='full')
        row = dict()
        row["_id"] = sym
        row[sym] = list()

        for k, v in data.items():
            if is_in_range(k):
                stock_info = dict()
                stock_info["date"] = k
                stock_info["price"] = data[k]['2. high']
                row[sym].append(stock_info)
        row[sym].sort(key=operator.itemgetter('date'))
        return row

    except ValueError as e:
        print("Could not fetch historic data for: %s. Err: %s ", sym, e)
        return []
    except TypeError as e:
        print("Ticker symbols must be string. Err ", e)
        return []



def get_symbols():
    """
    getSymbols: gets the stock symbols from Nasdaq csv file.
    :return: list, standard stock ticker symbol list
    """
    symbols_list = []
    with open('../DataSets/symbols.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skips headers
        for row in reader:
            symbols_list.append(row[0])
    return symbols_list


def persist_data(row):
    """
    persist_data writes a row to mongo DB.
    :param row: dict for a stock symbol. Key is the ticker symbol, value is the list of stock prices for last 180 days
    :return: None
    """
    print(row)
    if row is not None:
        posts.insert_one(row)


def main():
    """
    main collector function. It collects historic stock_price data for all NASDAQ symbols and writes it to
    mongo DB. We expect to run collector in the background every night to refresh the stock price data in mongo DB.
    :return: None
    """
    symbols = get_symbols()
    for symbol in symbols:
        row = fetch_historic_data(symbol)
        print(row)
        persist_data(row)
        # Sleep needed to not hit 3rd party API Rate limit.
        time.sleep(1)


if __name__ == "__main__":
    main()
