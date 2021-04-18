import json

from pika.adapters.blocking_connection import BlockingChannel

from mail_manager import MailManager
from metrics.topics import QUEUE_CONSUMER_BY_TEMPLATE, QUEUE_CONSUMER_BY_PRIORITY
from queue_manager import QueueManager
from schemas.queue_payload import QueuePayload


class Consumer:
    def __init__(self, mail_manager: MailManager, queue_channel: BlockingChannel, mails_per_hour: int):
        self.mail_manager = mail_manager
        self.queue_channel = queue_channel
        self.mails_per_hour = mails_per_hour

    def consume_mails_per_hour(self):
        self.queue_channel.queue_declare(queue=QueueManager.QUEUE_NAME, arguments={'x-max-priority': 255})

        for i in range(0, self.mails_per_hour):
            method, properties, body = self.queue_channel.basic_get(QueueManager.QUEUE_NAME, auto_ack=True)
            if body is None:
                continue

            payload = QueuePayload(**json.loads(body))

            QUEUE_CONSUMER_BY_TEMPLATE.labels(payload.template.value).inc()
            QUEUE_CONSUMER_BY_PRIORITY.labels(properties.priority).inc()

            # self.mail_manager.send_mail(payload.recipient, payload.mail_params, payload.template)

    def consume_send_last_mails(self):
        self.queue_channel.queue_declare(queue=QueueManager.QUEUE_NAME, arguments={'x-max-priority': 255})
        available_credits = self.mail_manager.get_available_credits()

        for i in range(0, available_credits):
            method, properties, body = self.queue_channel.basic_get(QueueManager.QUEUE_NAME, auto_ack=True)
            if body is None:
                continue

            payload = QueuePayload(**json.loads(body))

            QUEUE_CONSUMER_BY_TEMPLATE.labels(payload.template.value).inc()
            QUEUE_CONSUMER_BY_PRIORITY.labels(properties.priority).inc()

            # self.mail_manager.send_mail(payload.recipient, payload.mail_params, payload.template)
