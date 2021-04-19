import logging
from unittest import TestCase

import dotenv

logging.basicConfig(level=logging.DEBUG)


class Test(TestCase):

    def setUp(self):
        dotenv.load_dotenv()

    def test_push_arrivals_and_departures(self):
        import main
        main.push_arrivals_and_departures()

