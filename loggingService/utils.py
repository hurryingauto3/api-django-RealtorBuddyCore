import requests
from APIRealtorBuddyCore.config import SLACK_LOGGING_TOKEN


def sendHTTPLogToSlackChannel(
    body: str,
):

    url = "https://slack.com/api/chat.postMessage"
    payload = {
        "channel": "C077VLD98AG",
        "text": body,
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + SLACK_LOGGING_TOKEN,
    }

    r = requests.post(url, json=payload, headers=headers, timeout=30)

    if r.status_code == 200:
        return True
