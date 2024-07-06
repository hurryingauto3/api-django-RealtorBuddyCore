import datetime
from django.db import transaction
from celery import shared_task
from .models import client, clientEmailDefinition, clientEmailOutReachRuleset
from .utils import send_email_to_client, check_email_for_replies
import logging

logger = logging.getLogger(__name__)


@shared_task(name="clientEmailOutreachDriver")
def clientEmailOutreachDriver():

    clients = client.objects.filter(replied=False).order_by("last_contacted")
    emailDefinitions = clientEmailDefinition.objects.all()
    emailRulesets = clientEmailOutReachRuleset.objects.all()
    maxEmailStage = max([emailDefinition.key for emailDefinition in emailDefinitions])

    new_clients_count = 0
    follow_up_clients_count = 0

    for client_ in clients:
        if client_.contacted_times > maxEmailStage:
            continue

        else:
            contacted_times = client.contacted_times + 1
            email_type = emailDefinitions.objects.get(key=contacted_times)

            if (
                contacted_times == 0
                and new_clients_count < emailRulesets.new_clients_daily
            ):

                new_clients_count += 1
                clientEmailOutreach.apply_async(args=[client.id, email_type.id])

            else:
                past_due = (
                    datetime.datetime.now().date() - client.last_contacted
                    > datetime.timedelta(days=email_type.days_wait)
                )
                if (
                    past_due
                    and follow_up_clients_count < emailRulesets.follow_up_clients_daily
                ):
                    if (
                        not email_type.weekends
                        and datetime.datetime.now().weekday() in [5, 6]
                    ):
                        continue
                    else:
                        follow_up_clients_count += 1
                        clientEmailOutreach.apply_async(args=[client.id, email_type.id])


@shared_task(name="clientEmailOutreach")
def clientEmailOutreach(client_id, email_type_id):
    try:
        # Start a database transaction
        with transaction.atomic():
            # Fetch the client and email type from the database correctly using `get()` instead of `filter()`
            client_ = client.objects.get(id=client_id)

            # Send the email (placeholder for email sending logic)
            sent = send_email_to_client(
                client_.name, client_.email, email_type_id, user="ashir"
            )

            if sent:
                # Update client details
                client_.contacted_times += 1
                client_.last_contacted = datetime.datetime.now()
                client_.save()

                # Logging the action
                logger.info(
                    f"Email sent to {client_.name} <{client_.email}> for {email_type_id}."
                )
            else:
                logger.error(
                    f"Failed to send email to {client_.name} <{client_.email}> for {email_type_id}."
                )

    except client.DoesNotExist:
        print("Client not found.")
    except clientEmailPrediction.DoesNotExist:
        print("Email type definition not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


@shared_task(name="checkForReplies")
def checkForReplies():
    clients = client.objects.get(replied=False)
    for client_ in clients:
        # Check for replies (placeholder for email checking logic)
        replied = check_email_for_replies(client_.email)
        if replied:
            client_.replied = True
            client_.save()
            logger.info(f"Client {client_.name} <{client_.email}> has replied.")
        else:
            logger.info(f"No replies from {client_.name} <{client_.email}>.")
