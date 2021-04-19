import logging
from datetime import datetime, timezone, timedelta

import firebase_admin
from box import Box
from core.notification_message_templates import generate_notification_message, ARRIVALS_AND_DEPARTURES
from core.slack_message import send_slack_message
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': "trentiemeciel",
})

db = firestore.client()

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
    today = datetime.now(tz=timezone(timedelta(hours=2))) \
        .replace(hour=0, minute=0, second=0, microsecond=0)
    request_arrivals = db.collection_group('requests') \
        .where('state', "==", "CONFIRMED") \
        .where('arrival_date', '==', today) \
        .stream()
    request_departures = db.collection_group('requests') \
        .where('state', "==", "CONFIRMED") \
        .where('departure_date', '==', today) \
        .stream()

    def request_to_pax_name(doc):
        return Box(doc.reference.parent.parent.get().to_dict()).name

    def requests_to_pax_names(query):
        return (request_to_pax_name(doc) for doc in query)

    arrivals = requests_to_pax_names(request_arrivals)
    departures = requests_to_pax_names(request_departures)

    data = {
        "arrivals": arrivals,
        "departures": departures
    }
    notification_message = generate_notification_message(ARRIVALS_AND_DEPARTURES, data)
    send_slack_message(notification_message)
