from typing import Dict, List

import requests
from dateutil.relativedelta import relativedelta

from schemas.mail_params import MailParams
from schemas.recipient import Recipient
from schemas.template import Template


class MailManager:
    def __init__(self, api_key: str, url: str):
        self.api_key = api_key
        self.url = url

    def _send_email(self, to: List[Recipient], template: Template, params: Dict[str, str] = None):
        json = {
            'templateId': template.value,
            'to': [user.dict() for user in to],
        }
        if params is not None:
            json['params'] = params
        response = requests.post(self.url, headers={'api-key': self.api_key}, json=json)

        if not 200 <= response.status_code < 300:
            print(str(response.json()))
            return False
        return True

    def send_confirmation_to_mentored(self, to: Recipient, mail_metadata: MailParams):
        params = {
            'MENTOR_NAME': mail_metadata.mentor_name,
            'MENTORING_DATE': mail_metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': mail_metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': mail_metadata.mentored_name,
            'MENTOR_ID': mail_metadata.mentor_id
        }
        return self._send_email([to], Template.CONFIRMATION_TO_MENTORED, params)

    def send_confirmation_to_mentor(self, to: Recipient, mail_metadata: MailParams):
        params = {
            'MENTOR_NAME': mail_metadata.mentor_name,
            'MENTORING_DATE': mail_metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': mail_metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': mail_metadata.mentored_name,
            'MENTORED_ID': mail_metadata.mentored_id
        }
        return self._send_email([to], Template.CONFIRMATION_TO_MENTOR, params)

    def notify_subscribed_users_not_selected(self, to: Recipient, mail_metadata: MailParams):
        params = {
            'MENTOR_NAME': mail_metadata.mentor_name,
            'MENTORING_DATE': mail_metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': mail_metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': mail_metadata.mentored_name
        }
        return self._send_email([to], Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED, params)

    def notify_subscribed_users_of_mentoring_canceled(self, to: Recipient, mail_metadata: MailParams):
        params = {
            'MENTOR_NAME': mail_metadata.mentor_name,
            'MENTOR_ID': mail_metadata.mentor_id,
            'MENTORING_DATE': mail_metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': mail_metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': mail_metadata.mentored_name
        }
        return self._send_email([to], Template.NOTIFY_SUBSCRIBED_USERS_MENTORING_CANCELED, params)

    def notify_mentor_of_mentored_leaving(self, to: Recipient, mail_metadata: MailParams):
        params = {
            'MENTOR_NAME': mail_metadata.mentor_name,
            'MENTORED_NAME': mail_metadata.mentored_name,
            'MENTORING_DATE_LIMIT': (mail_metadata.mentoring_datetime - relativedelta(days=1)).strftime('%d/%m/%Y'),
            'MENTORING_DATE': mail_metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': mail_metadata.mentoring_datetime.strftime('%H:%M')
        }
        return self._send_email([to], Template.NOTIFY_MENTOR_OF_MENTORED_LEAVING, params)
