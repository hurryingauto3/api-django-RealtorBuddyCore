import requests
from APIRealtorBuddyCore.config import SLACK_BA_TOKEN

def validateBuildingDataFromSlack(
    building_id,
    building_name,
    user_query,
    from_number,
):

    building_url = (
        f"https://api.realtor-buddy.com/buildings/building/{building_id}"
    )
    url = "https://slack.com/api/chat.postMessage"
    payload = {
        "channel": "C0740BAAF0E",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"A client is requesting information for *<{building_url}|{building_name}>*",
                },
            },
            {
                "type": "section",
                "fields": [{"type": "mrkdwn", "text": f'*Message:*\n"{user_query}"'}],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Updated",
                        },
                        "style": "primary",
                        "value": f"{building_id}_{from_number}",
                    }
                ],
            },
        ],
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Bearer " + SLACK_BA_TOKEN,
    }

    r = requests.post(url, json=payload, headers=headers, timeout=30)

    if r.status_code == 200:
        return True