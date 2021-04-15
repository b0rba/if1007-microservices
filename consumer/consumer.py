import json

from mail_manager import MailManager
from schemas.queue_payload import QueuePayload


class Consumer:
    def __init__(self, mail_manager: MailManager):
        self.mail_manager = mail_manager

    def consume(self, queue_payload: bytes):
        try:
            payload = QueuePayload(**json.loads(queue_payload))
            print(payload.dict())
            # self.mail_manager.send_mail(payload.recipient, payload.mail_params, payload.template)
        except Exception as e:
            print(e)
