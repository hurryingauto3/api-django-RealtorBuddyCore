from django.db import transaction
import random
import datetime

from celery import shared_task
from django.db.models import Q
from celery.utils.log import get_task_logger
from .models import (
    client,
    clientEmailDefinition,
    clientEmailOutReachRuleset,
    clientEmailLogs,
)
from .utils import send_email_to_client, check_email_for_replies

logger = get_task_logger(__name__)


@shared_task(name="clientEmailOutreachDriver")
def clientEmailOutreachDriver():
    clients = client.objects.filter(replied=False)
    logger.info(f"Starting email outreach for {len(clients)} clients.")
    emailDefinitions = {ed.key: ed for ed in clientEmailDefinition.objects.all()}
    emailRulesets = clientEmailOutReachRuleset.objects.first()
    maxEmailStage = max(emailDefinitions.keys())

    new_clients_count = 0
    follow_up_clients_count = 0

    for client_ in clients:

        logger.info(
            f"Processing client {client_.name} <{client_.email}>. Times contacted: {client_.contacted_times}. Last contacted: {client_.last_contacted}."
        )

        if client_.contacted_times > maxEmailStage:
            continue

        contacted_times = client_.contacted_times + 1
        logger.info(f"Email stage: {contacted_times}.")
        email_type = emailDefinitions.get(contacted_times)

        if not email_type:
            continue  # Skip if no email type for this contact stage

        if contacted_times == 1 and new_clients_count < emailRulesets.new_clients_daily:
            logger.info(f"Sending cold email to {client_.name} <{client_.email}>.")
            new_clients_count += 1
            # clientEmailOutreach.apply_async(args=[client_.id, email_type.key])
            clientEmailOutreach(client_.id, email_type.key)

        else:

            if not client_.last_contacted:
                logger.info(
                    f"Client {client_.name} <{client_.email}> has not been contacted before."
                )
                continue

            past_due = (
                datetime.datetime.now() - client_.last_contacted
            ).days > email_type.days_wait

            if (
                past_due
                and follow_up_clients_count < emailRulesets.follow_up_clients_daily
            ):
                if not email_type.weekends and datetime.datetime.now().weekday() in [
                    5,
                    6,
                ]:
                    continue

                logger.info(
                    f"Sending follow-up email to {client_.name} <{client_.email}>."
                )
                follow_up_clients_count += 1
                # clientEmailOutreach.apply_async(args=[client_.id, email_type.key])
                clientEmailOutreach(client_.id, email_type.key)


@shared_task(name="clientEmailOutreach")
def clientEmailOutreach(client_id, email_type_id):
    try:
        with transaction.atomic():
            client_ = client.objects.select_for_update().get(id=client_id)
            
            replied = check_email_for_replies(client_.email)
            if replied:
                client_.replied = True
                client.replied_at = datetime.datetime.now()
                client_.save()
                logger.info(f"Client {client_.name} <{client_.email}> has replied.")
                
                return False
            
            emails = clientEmailDefinition.objects.filter(Q(key=email_type_id))
            email = random.choice(emails)

            sent = send_email_to_client(
                client_.name, client_.email, email.id, user="ashir"
            )

            if sent:
                client_.contacted_times += 1
                client_.last_contacted = datetime.datetime.now()
                client_.save()

                email_log = clientEmailLogs(client=client_, email=email)
                email_log.save()

                logger.info(
                    f"Email sent to {client_.name} <{client_.email}> for email type {email_type_id}."
                )
                
                return sent

            else:
                logger.error(
                    f"Failed to send email to {client_.name} <{client_.email}> for email type {email_type_id}."
                )
                
                return False
            

    except client.DoesNotExist:
        logger.error("Client not found.")
    except clientEmailDefinition.DoesNotExist:
        logger.error("Email type definition not found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

