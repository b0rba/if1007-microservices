from datetime import datetime

from pydantic import BaseModel

from schemas.mail_params import MailParams
from schemas.recipient import Recipient
from schemas.template import Template


class QueuePayload(BaseModel):
    mail_params: MailParams
    recipient: Recipient
    template: Template

    def get_priority_value(self):
        mentoring_datetime = self.mail_params.mentoring_datetime
        days_difference = (mentoring_datetime.replace(tzinfo=None) - datetime.now()).days + 1
        if days_difference > 199:
            return 1
        return 200 - days_difference
