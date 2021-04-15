import unittest
from datetime import datetime
from uuid import uuid4

from dateutil.relativedelta import relativedelta

from schemas.mail_params import MailParams
from schemas.queue_payload import QueuePayload
from schemas.recipient import Recipient
from schemas.template import Template


class TestQueuePayload(unittest.TestCase):
    def test_get_priority_value(self):
        mentor_name = 'xablau'
        mentored_name = 'xalala'
        mentored_email = 'xalala@gmail.com'

        recipient = Recipient(
            name=mentored_name,
            email=mentored_email
        )
        template = Template.CONFIRMATION_TO_MENTORED

        mentoring_days_from_now = 250
        mail_params = MailParams(
            mentor_name=mentor_name,
            mentoring_datetime=datetime.now() + relativedelta(days=mentoring_days_from_now),
            mentored_name=mentored_name,
            mentor_id=str(uuid4())
        )

        queue = QueuePayload(mail_params=mail_params, recipient=recipient, template=template)
        self.assertEqual(1, queue.get_priority_value())

        mentoring_days_from_now = 0
        queue.mail_params.mentoring_datetime = datetime.now() + relativedelta(days=mentoring_days_from_now)
        self.assertEqual(200, queue.get_priority_value())

        mentoring_days_from_now = -2
        queue.mail_params.mentoring_datetime = datetime.now() + relativedelta(days=mentoring_days_from_now)
        self.assertEqual(202, queue.get_priority_value())


if __name__ == '__main__':
    unittest.main()
