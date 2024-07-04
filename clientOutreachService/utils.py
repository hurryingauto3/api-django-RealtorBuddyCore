import base64
import json
from django.core.mail import EmailMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from APIRealtorBuddyCore.config import GMAIL_SERVICE_ACCOUNT
from .models import clientEmailDefinition
import base64
from email.mime.text import MIMEText


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
        mime_message = MIMEText(message.body, _subtype="plain")
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


def construct_email(to, message_id, context):
    # Simulated retrieval of email template data
    email_data = get_email_template(message_id, context)
    if not email_data:
        raise ValueError("Invalid message_id or missing email template")

    # Create an EmailMessage object
    email = EmailMessage(
        subject=email_data["subject"],
        body=email_data["body"],
        to=[to],
    )
    return email


def get_email_template(message_id, context):

    email = clientEmailDefinition.objects.get(key=message_id)
    subject, body = email.render_email(context)
    return {"subject": subject, "body": body}

    # templates = {
    #     "1": {"subject": "Welcome!", "body": "Thank you for joining our platform."},
    #     "2": {"subject": "Reminder", "body": "Just a reminder about our upcoming event."},
    # }
    # return templates.get(str(message_id))


def get_user_info(email):
    # This is a placeholder function. You should implement it to return user information.
    # For example, query from a database:
    user_info = {
        "ali@realtor-buddy.com": "Ali Hamza",
        "ashir@realtor-buddy.com": "Ashir Ghori",
    }
    return user_info.get(email, None)
