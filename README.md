## Stock Profit maximization

### Description
This project exposes a REST URL on localhost:8080 which accepts
a JSON encoded query having the NASDAQ ticker symbol.
It returns a JSON response containing the buy and sell date for
maximum profit in the past 180 days.

### Architecture
```
            ---------------
            |             |
            |  API Server |
            |             |
            ---------------
                   |
                   |
                   V
            ---------------
            |             |
            | Mongo DB    |
            |             |
            ---------------
                   ^
                   |
                   |

            ----------------
            |              |
            | Collector    |
            |              |
            ----------------
```

### Services
1. `API Server`
Is implemented as a REST Service using flask
It accepts a JSON encoded query request containing the stock ticker symbol.

`Request`
```
{"stock":"FB"}
```

`Response`
```
{
  "best_buy_price": 155.56,
  "max_profit": 39.75999999999999,
  "best_sell_price": 195.32,
  "buy": "2018-04-04",
  "sell": "2018-02-01"
}
```

The API Server will always have the last 180 days worth of stock
data for all NASDAQ stocks is present in the DB.

2. `Mongo DB`
Mongo DB is used to store sanitized historic data for all
NASDAQ stocks. We ensure that the data is sorted in asscending order
of date prior to storing it in the DB. This will ensure that
the API server is always working on the sorted data in time.
This will also prevent the API Server from doing the sort for every
request.
`Data Format`
```
{ "_id" : "FB", "FB" : [ { "price" : "179.8300", "date" : "2017-11-16" }...]}
```

3. `Collector`
Collector is what populates the stock information in the DB.
It parses a symbols.csv file which is downloaded from NASDAQ
website and fetches each stock's historic data from alphavantage
API. Changing the data source will involve modifying only the collector
service. We expect the collector service to run as a nightly
batched job to populate the DB. This will ensure that the data
stored will always be for the last 180 days and API server
can function with the assumption that the DB will always be kept updated.

I feel this approach is acceptable as we have some 3000 odd stocks
and it won't be computationally too expensive to run this on a
nightly basis as the markets close.

Currently it takes about an hour to fetch all the stock information.
There are two reasons why it takes so long.
    1. Alpha vantage API has a rate limit so we have to sleep for a
    second between API calls.
    2. Alpha vantage API doesn't have the concept the response size. It either gives a compact version with
    100 datapoints or a full data set for past 20 years. Requesting
    for all the past 20 years of data results in a large response, we
    truncate this for last 180 days, sort it in time and persist this information
    in Mongo DB

### Dependencies
We need the following packages.
1. Flask
2. pymongo
3. alpha_vantage
4. Running mongo DB on localhost:27017

### Code structure.
All the unit tests can be found in the corresponding test.py files in each service.

### Sample input/output
`Request`

```
curl -s -d'{"stock":"FB"}' -X POST -H "Content-Type:application/json" localhost:8080 | jq .
```

`Response`
```
{
  "best_buy_price": 155.56,
  "max_profit": 39.75999999999999,
  "best_sell_price": 195.32,
  "buy": "2018-04-04",
  "sell": "2018-02-01"
}
```

### Future enhancements.
1. We should build a Redis cache as a peer to API Server, which
can cache the computed results. The repeated queries on the same
stock symbol will be faster.
2. Make each of these services into containers and deploy in
Kubernetes for managing replication and scale.
3. Optimization around data collection. Collecing all 180 days
worth of data daily and overwriting the DB seems sub optimal.
We can implement a continuous moving datapoints in the DB.
4. Collector currently relies on a static symbols file, it means
the responsibility of keeping this file is delegated to the admin.
Collector itself can make an API call to enumerate all the stocks
5. Collector also needs to support more exchanges than just NASDAQ

