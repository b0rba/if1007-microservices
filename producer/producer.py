from datetime import datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta
from faker import Faker

from schemas.mail_params import MailParams
from schemas.queue_payload import QueuePayload
from schemas.recipient import Recipient
from schemas.template import Template


class Producer:
    def __init__(self):
        self.fake = Faker(locale='pt_br')

    def produce_confirmation_to_mentored(self):
        mentored_name = self.fake.name()
        mail_params = MailParams(
            mentor_name=self.fake.name(),
            mentoring_datetime=datetime.now() + relativedelta(days=self.fake.random.randint(0, 10)),
            mentored_name=mentored_name,
            mentor_id=str(uuid4())
        )

        recipient = Recipient(
            name=mentored_name,
            email=self.fake.email()
        )
        template = Template.CONFIRMATION_TO_MENTORED
        return QueuePayload(mail_params=mail_params, recipient=recipient, template=template)

    def produce_confirmation_to_mentor(self):
        mentor_name = self.fake.name()
        mail_params = MailParams(
            mentor_name=mentor_name,
            mentoring_datetime=datetime.now() + relativedelta(days=self.fake.random.randint(0, 10)),
            mentored_name=self.fake.name(),
            mentored_id=str(uuid4())
        )

        recipient = Recipient(
            name=mentor_name,
            email=self.fake.email()
        )
        template = Template.CONFIRMATION_TO_MENTOR
        return QueuePayload(mail_params=mail_params, recipient=recipient, template=template)

    def produce_notify_subscribed_users_not_selected(self):
        mentored_name = self.fake.name()
        mail_params = MailParams(
            mentor_name=self.fake.name(),
            mentoring_datetime=datetime.now() + relativedelta(days=self.fake.random.randint(0, 10)),
            mentored_name=mentored_name,
        )

        recipient = Recipient(
            name=mentored_name,
            email=self.fake.email()
        )
        template = Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED
        return QueuePayload(mail_params=mail_params, recipient=recipient, template=template)

    def produce_notify_subscribed_users_of_mentoring_canceled(self):
        mentored_name = self.fake.name()
        mail_params = MailParams(
            mentor_name=self.fake.name(),
            mentoring_datetime=datetime.now() + relativedelta(days=self.fake.random.randint(0, 10)),
            mentored_name=mentored_name,
        )

        recipient = Recipient(
            name=mentored_name,
            email=self.fake.email()
        )
        template = Template.NOTIFY_SUBSCRIBED_USERS_MENTORING_CANCELED
        return QueuePayload(mail_params=mail_params, recipient=recipient, template=template)

    def produce_notify_mentor_of_mentored_leaving(self):
        mentor_name = self.fake.name()
        mail_params = MailParams(
            mentor_name=mentor_name,
            mentoring_datetime=datetime.now() + relativedelta(days=self.fake.random.randint(0, 10)),
            mentored_name=self.fake.name(),
            mentored_id=str(uuid4())
        )

        recipient = Recipient(
            name=mentor_name,
            email=self.fake.email()
        )
        template = Template.NOTIFY_MENTOR_OF_MENTORED_LEAVING
        return QueuePayload(mail_params=mail_params, recipient=recipient, template=template)
