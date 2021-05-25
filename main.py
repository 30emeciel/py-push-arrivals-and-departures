import logging
from datetime import datetime, timezone, timedelta

from box import Box
from core import firestore_client
from core.slack_message import SlackSender
from core.tpl import render

PARIS_TZ = timezone(timedelta(hours=2))

db = firestore_client.db()
slack_sender = SlackSender()

log = logging.getLogger(__name__)


def from_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # pubsub_message = base64.b64decode(event['data']).decode('utf-8')
    # print(pubsub_message)
    push_arrivals_and_departures()


def push_arrivals_and_departures():
    # TODO: fix timestamp in DB!
    today = datetime.now(tz=PARIS_TZ) \
        .replace(hour=0, minute=0, second=0, microsecond=0)
    push_arrivals_and_departures_sub(today)


def push_arrivals_and_departures_sub(today):
    request_arrivals = db.collection_group('requests') \
        .where('state', "==", "CONFIRMED") \
        .where('arrival_date', '==', today) \
        .stream()
    request_departures = db.collection_group('requests') \
        .where('state', "==", "CONFIRMED") \
        .where('departure_date', '==', today) \
        .stream()

    def reservation_data_with_time(r):
        pax = Box(r.reference.parent.parent.get().to_dict())
        r = Box(r.to_dict(), default_box=True, default_box_attr="")
        return f"{pax.name} ({r.arrival_time})"

    def reservation_data(r):
        pax = Box(r.reference.parent.parent.get().to_dict())
        return f"{pax.name}"

    def reservation_query_to_data(query):
        return [reservation_data_with_time(r) for r in query]

    arrivals = reservation_query_to_data(request_arrivals)
    departures = [reservation_data(r) for r in request_departures]
    data = {
        "arrivals": arrivals,
        "departures": departures
    }
    slack_message = render("arrivals_and_departures_fr.txt", data).strip()
    if slack_message:
        slack_sender.send_slack_message(slack_message)
