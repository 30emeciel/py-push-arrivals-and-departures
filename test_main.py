import logging
from datetime import datetime

import pytest

import dotenv

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(autouse=True)
def setup():
    dotenv.load_dotenv()


def test_push_arrivals_and_departures():
    import main
    main.push_arrivals_and_departures()


def test_push_arrivals_and_departures_sub():
    import main
    today = datetime(2021, 5, 24, 00, 00, 00, tzinfo=main.PARIS_TZ)
    main.push_arrivals_and_departures_sub(today)
