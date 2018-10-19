import unittest
from Collector import *


class CollectorInRangeTest(unittest.TestCase):
    def test_is_in_range(self):
        now = datetime.datetime.today().strftime("%Y-%m-%d")
        self.assertEqual(is_in_range(now), True)

    def test_not_in_range(self):
        epoch = '1970-01-01'
        self.assertEqual(is_in_range(epoch), False)

    def test_in_range_empty(self):
        self.assertEqual(is_in_range(""), False)

    def test_in_range_invalid_input(self):
        self.assertEqual(is_in_range(42), False)

    def test_in_range_exact_end_match(self):
        now = datetime.datetime.today()
        delta = datetime.timedelta(days=NUMBER_OF_DAYS)
        exact_end_match = now - delta
        exact_end_match_date = exact_end_match.strftime("%Y-%m-%d")
        self.assertEqual(is_in_range(exact_end_match_date), True)


class CollectorFetchHistoricDataTest(unittest.TestCase):
    def test_fetch_historic_data_for_goog(self):
        # Repeated runs of the test should not trigger API Rate limiting.
        time.sleep(1)
        data = fetch_historic_data("GOOG")
        self.assertGreater(len(data), 0)

    def test_fetch_historic_data_invalid_ticker(self):
        # Repeated runs of the test should not trigger API Rate limiting.
        time.sleep(1)
        data = fetch_historic_data("INVALID_TICKER")
        self.assertEqual(len(data), 0)

    def test_fetch_historic_data_invalid_ticker_type(self):
        # Repeated runs of the test should not trigger API Rate limiting.
        time.sleep(1)
        data = fetch_historic_data(42)
        self.assertEqual(len(data), 0)


class CollectorGetSymbolsTest(unittest.TestCase):
    def test_get_symbols(self):
        symbols = get_symbols()
        self.assertGreater(len(symbols), 0)
        self.assertEqual("GOOG" in symbols, True)
        self.assertEqual("INVALID_TICKER" in symbols, False)


# ToDo
# class CollectorPersistDataTest(unittest.TestCase):
#     def test_persist_data(self):

if __name__ == '__main__':
    unittest.main()
