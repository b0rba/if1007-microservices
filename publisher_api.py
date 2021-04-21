import json
from os import environ

import pika
from fastapi import FastAPI
from starlette import status

from queue_manager import QueueManager
from schemas.mail_params import ConfirmationToMentorParams, MailParams, ConfirmationToMentoredParams, \
    NotifyMentorOfMentoredLeavingParams, NotifySubscribedUserNotSelectedParams, \
    NotifySubscribedUserMentoringCanceledParams
from schemas.queue_payload import QueuePayload
from schemas.recipient import Recipient
from schemas.template import Template

app = FastAPI()


QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@localhost:5672/%2f')
queue_manager = QueueManager(QUEUE_SERVICE_URL)

channel = queue_manager.channel()
channel.queue_declare(queue=QueueManager.QUEUE_NAME, arguments={'x-max-priority': 255})


def publish(mail_params: MailParams, recipient: Recipient, template: Template) -> QueuePayload:
    payload = QueuePayload(mail_params=mail_params, recipient=recipient, template=template)
    channel.basic_publish(exchange='', routing_key=QueueManager.QUEUE_NAME,
                          body=json.dumps(payload.dict(), default=str),
                          properties=pika.BasicProperties(priority=payload.get_priority_value()))
    return payload


@app.post('/confirmation-to-mentor', status_code=status.HTTP_200_OK, response_model=QueuePayload)
async def publish_confirmation_to_mentor(params: ConfirmationToMentorParams):
    mail_params = MailParams(**params.dict())
    recipient = Recipient(name=params.mentor_name, email=params.mentor_email)
    template = Template.CONFIRMATION_TO_MENTOR
    return publish(mail_params, recipient, template)


@app.post('/confirmation-to-mentored')
async def publish_confirmation_to_mentored(params: ConfirmationToMentoredParams):
    mail_params = MailParams(**params.dict())
    recipient = Recipient(name=params.mentored_name, email=params.mentored_email)
    template = Template.CONFIRMATION_TO_MENTORED
    return publish(mail_params, recipient, template)


@app.post('/notify-mentor-of-mentored-leaving')
async def publish_notify_mentor_of_mentored_leaving(params: NotifyMentorOfMentoredLeavingParams):
    mail_params = MailParams(**params.dict())
    recipient = Recipient(name=params.mentor_name, email=params.mentor_email)
    template = Template.NOTIFY_MENTOR_OF_MENTORED_LEAVING
    return publish(mail_params, recipient, template)


@app.post('/notify-subscribed-users-not-selected')
async def publish_notify_subscribed_users_not_selected(params: NotifySubscribedUserNotSelectedParams):
    mail_params = MailParams(**params.dict())
    recipient = Recipient(name=params.mentored_name, email=params.mentored_email)
    template = Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED
    return publish(mail_params, recipient, template)


@app.post('/notify-subscribed-users-of-mentoring-canceled')
async def publish_notify_subscribed_users_not_selected(params: NotifySubscribedUserMentoringCanceledParams):
    mail_params = MailParams(**params.dict())
    recipient = Recipient(name=params.mentored_name, email=params.mentored_email)
    template = Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED
    return publish(mail_params, recipient, template)


@app.on_event('shutdown')
def shutdown_event():
    queue_manager.close()
