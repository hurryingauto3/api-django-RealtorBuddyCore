import traceback
import base64
import json


from django.core.mail import EmailMessage
from django.template import engines

from google.oauth2 import service_account
from googleapiclient.discovery import build
from APIRealtorBuddyCore.config import GMAIL_SERVICE_ACCOUNT
from .models import clientEmailDefinition

import logging
import base64
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


class GmailServiceAccountAPI:

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.labels",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/gmail.insert",
        "https://www.googleapis.com/auth/gmail.modify",
    ]

    def __init__(self, delegated_user):
        # Get the service account info from the environment variable
        service_account_info = json.loads(GMAIL_SERVICE_ACCOUNT)

        # Create credentials from the service account info
        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=self.SCOPES
        )

        # Delegated user email
        self.delegated_user = delegated_user

        # Delegate domain-wide authority to the service account
        self.delegated_credentials = self.credentials.with_subject(self.delegated_user)

        # Build the Gmail API service
        self.service = build("gmail", "v1", credentials=self.delegated_credentials)

    def list_email(self, query=""):
        # List messages
        results = self.service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])
        return messages

    def read_email(self, msg_id):
        try:
            message = (
                self.service.users().messages().get(userId="me", id=msg_id).execute()
            )
            email_data = {
                "id": message.get("id"),
                "threadId": message.get("threadId"),
                "labelIds": message.get("labelIds"),
                "snippet": message.get("snippet"),
                "payload": {
                    "headers": message.get("payload", {}).get("headers", []),
                    "body": self._get_body(message.get("payload", {})),
                },
            }
            return email_data
        except Exception as error:
            raise Exception(f"An error occurred: {error}")

    def _get_body(self, payload):
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    body += base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8"
                    )
                elif part["mimeType"] == "multipart/alternative":
                    body += self._get_body(part)

        elif "body" in payload and "data" in payload["body"]:
            body += base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
        return body

    def send_email(self, message):
        # Create a MIMEText object
        mime_message = MIMEText(message.body, _subtype="html")
        mime_message["to"] = message.to[0]
        mime_message["from"] = (
            f"{get_user_info(self.delegated_user)} <{self.delegated_user}>"
        )
        mime_message["subject"] = message.subject

        # Encode the MIMEText object into a base64url encoded string
        raw = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()

        # Prepare the message dictionary for the Gmail API
        message = {"raw": raw}

        # Send the email
        sent_message = (
            self.service.users().messages().send(userId="me", body=message).execute()
        )
        return sent_message

    def list_labels(self):
        # List labels
        results = self.service.users().labels().list().execute()
        labels = results.get("labels", [])
        return labels

    def modify_labels(self, msg_id, labels):
        # Modify labels on a message
        message = (
            self.service.users().messages().modify(id=msg_id, body=labels).execute()
        )
        return message


def construct_email(to, from_, message_id, context):
    # Simulated retrieval of email template data
    email_data = get_email_template(message_id, context)

    if not email_data:
        raise ValueError("Invalid message_id or missing email template")

    subject = email_data["subject"]
    body = get_body_html(
        email_data["body"], from_name=get_user_info(from_), from_email=from_
    )
    # Create an EmailMessage object
    email = EmailMessage(
        subject=subject,
        body=body,
        to=[to],
    )
    return email


def get_email_template(message_id, context):

    email = clientEmailDefinition.objects.get(id=message_id)
    subject, body = email.render_email(context)
    return {"subject": subject, "body": body}


def get_body_html(body_text, from_name, from_email):
    jinja2_engine = engines["jinja2"]  # Access the configured Jinja2 engine

    # Split the body text into lines if it's not already a list
    body_lines = body_text.split("\n") if isinstance(body_text, str) else body_text

    # Render the template
    template = jinja2_engine.get_template("email_template.html")
    return template.render(
        {"body": body_lines, "from_name": from_name, "from_email": from_email}
    )


def get_user_info(email):
    # This is a placeholder function. You should implement it to return user information.
    # For example, query from a database:
    user_info = {
        "ali@realtor-buddy.com": "Ali Hamza",
        "ashir@realtor-buddy.com": "Ashir Ghori",
    }
    return user_info.get(email, None)


def send_email_to_client(name, to, message_id, user="ashir"):
    # Get the GmailServiceAccountAPI instance
    user = f"{user}@realtor-buddy.com"
    gmail_service = GmailServiceAccountAPI(delegated_user=user)

    try:
        # Send the email
        to = f"{name} <{to}>"
        context = {
            "name": name.split(" ")[0],
            "number": """<a href="sms:+16562203831" stlye="color: ##242082">(656) 220 3831</a>""",
        }
        message = construct_email(to, user, message_id, context)
        sent = gmail_service.send_email(message)
        if sent:
            return True
    except Exception as e:
        logger.error(
            f"send_email_to_client: An error occurred: {e}, traceback: {traceback.format_exc()}"
        )
        return False


def check_email_for_replies(email, user="ashir"):
    # This is a placeholder function. You should implement it to check for email replies.
    user = f"{user}@realtor-buddy.com"
    gmail_service = GmailServiceAccountAPI(delegated_user=user)

    try:
        messages = gmail_service.list_email(query=f"from:{email}")
        return bool(messages)
    except Exception as e:
        logger.error(f"An error occurred: {e}, traceback: {e.with_traceback(None)}")
        return False
