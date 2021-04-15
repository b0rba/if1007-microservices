import unittest
from datetime import datetime
from typing import List
from unittest.mock import patch, MagicMock

from dateutil.relativedelta import relativedelta

from mail_manager import MailManager
from schemas.mail_params import MailParams
from schemas.recipient import Recipient
from schemas.template import Template
from tests import response_factory


class TestMailManager(unittest.TestCase):
    def setUp(self) -> None:
        self.url = 'https://api.sendinblue.com/v3'
        self.mail_manager = MailManager(
            api_key='xalala',
            url=self.url,
        )
        self.to = Recipient(name='xalala', email='xalala@gmail.com')
        self.receivers: List[Recipient] = [self.to]
        self.metadata = MailParams(mentor_name='xalala', mentoring_datetime=datetime(2012, 2, 28))

    @patch('requests.post', return_value=response_factory.get_valid_response())
    def test_send_email(self, post):
        template = Template.CONFIRMATION_TO_MENTOR

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTORING_DATE_LIMIT': (self.metadata.mentoring_datetime - relativedelta(days=1)).strftime('%d/%m/%Y')
        }

        json = {
            'templateId': template.value,
            'to': [user.dict() for user in self.receivers],
            'params': params
        }
        res = self.mail_manager._send_email([self.to], template, params)
        self.assertTrue(res)

        post.assert_called_once_with(f'{self.url}/smtp/email', headers={'api-key': self.mail_manager.api_key}, json=json)

    @patch('mail_manager.MailManager._send_email', return_value=True)
    def test_send_confirmation_to_mentored(self, send_email):
        res = self.mail_manager._send_confirmation_to_mentored(self.to, self.metadata)
        self.assertTrue(res)

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTOR_ID': self.metadata.mentor_id,
            'MENTORING_DATE': self.metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': self.metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': self.metadata.mentored_name
        }
        send_email.assert_called_once_with([self.to], Template.CONFIRMATION_TO_MENTORED, params)

    @patch('mail_manager.MailManager._send_email', return_value=True)
    def test_send_confirmation_to_mentor(self, send_email):
        res = self.mail_manager._send_confirmation_to_mentor(self.to, self.metadata)
        self.assertTrue(res)

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTORED_ID': self.metadata.mentor_id,
            'MENTORING_DATE': self.metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': self.metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': self.metadata.mentored_name
        }
        send_email.assert_called_once_with([self.to], Template.CONFIRMATION_TO_MENTOR, params)

    @patch('mail_manager.MailManager._send_email', return_value=True)
    def test_notify_subscribed_users_not_selected(self, send_email):
        res = self.mail_manager._notify_subscribed_users_not_selected(self.to, self.metadata)
        self.assertTrue(res)

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTORING_DATE': self.metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': self.metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': self.metadata.mentored_name
        }
        send_email.assert_called_once_with([self.to], Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED, params)

    @patch('mail_manager.MailManager._send_email', return_value=True)
    def test_notify_subscribed_users_of_mentoring_canceled(self, send_email):
        res = self.mail_manager._notify_subscribed_users_of_mentoring_canceled(self.to, self.metadata)
        self.assertTrue(res)

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTOR_ID': self.metadata.mentor_id,
            'MENTORING_DATE': self.metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': self.metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': self.metadata.mentored_name
        }
        send_email.assert_called_once_with([self.to], Template.NOTIFY_SUBSCRIBED_USERS_MENTORING_CANCELED, params)

    @patch('mail_manager.MailManager._send_email', return_value=True)
    def test_notify_mentor_of_mentored_leaving(self, send_email):
        res = self.mail_manager._notify_mentor_of_mentored_leaving(self.to, self.metadata)
        self.assertTrue(res)

        params = {
            'MENTOR_NAME': self.metadata.mentor_name,
            'MENTORING_DATE_LIMIT': (self.metadata.mentoring_datetime - relativedelta(days=1)).strftime('%d/%m/%Y'),
            'MENTORING_DATE': self.metadata.mentoring_datetime.strftime('%d/%m/%Y'),
            'MENTORING_HOUR': self.metadata.mentoring_datetime.strftime('%H:%M'),
            'MENTORED_NAME': self.metadata.mentored_name
        }
        send_email.assert_called_once_with([self.to], Template.NOTIFY_MENTOR_OF_MENTORED_LEAVING, params)

    @patch('requests.get', return_value=response_factory.get_valid_account_response())
    def test_get_available_credits(self, get: MagicMock):
        mock_credits = 300
        get.return_value = response_factory.get_valid_account_response(mock_credits)
        res = self.mail_manager.get_available_credits()
        self.assertEqual(mock_credits, res)

        get.assert_called_once_with(f'{self.url}/account', headers={'api-key': self.mail_manager.api_key})

    @patch('mail_manager.MailManager._send_confirmation_to_mentored')
    @patch('mail_manager.MailManager._send_confirmation_to_mentor')
    @patch('mail_manager.MailManager._notify_subscribed_users_not_selected')
    @patch('mail_manager.MailManager._notify_subscribed_users_of_mentoring_canceled')
    @patch('mail_manager.MailManager._notify_mentor_of_mentored_leaving')
    def test_send_mail_confirmation_to_mentored(
            self, _notify_mentor_of_mentored_leaving, _notify_subscribed_users_of_mentoring_canceled,
            _notify_subscribed_users_not_selected, _send_confirmation_to_mentor, _send_confirmation_to_mentored):
        template = Template.CONFIRMATION_TO_MENTORED
        self.mail_manager.send_mail(self.to, self.metadata, template)
        _send_confirmation_to_mentored.assert_called_once_with(self.to, self.metadata)
        _send_confirmation_to_mentor.assert_not_called()
        _notify_subscribed_users_not_selected.assert_not_called()
        _notify_subscribed_users_of_mentoring_canceled.assert_not_called()
        _notify_mentor_of_mentored_leaving.assert_not_called()

    @patch('mail_manager.MailManager._send_confirmation_to_mentored')
    @patch('mail_manager.MailManager._send_confirmation_to_mentor')
    @patch('mail_manager.MailManager._notify_subscribed_users_not_selected')
    @patch('mail_manager.MailManager._notify_subscribed_users_of_mentoring_canceled')
    @patch('mail_manager.MailManager._notify_mentor_of_mentored_leaving')
    def test_send_mail_confirmation_to_mentor(
            self, _notify_mentor_of_mentored_leaving, _notify_subscribed_users_of_mentoring_canceled,
            _notify_subscribed_users_not_selected, _send_confirmation_to_mentor, _send_confirmation_to_mentored):
        template = Template.CONFIRMATION_TO_MENTOR
        self.mail_manager.send_mail(self.to, self.metadata, template)
        _send_confirmation_to_mentored.assert_not_called()
        _send_confirmation_to_mentor.assert_called_once_with(self.to, self.metadata)
        _notify_subscribed_users_not_selected.assert_not_called()
        _notify_subscribed_users_of_mentoring_canceled.assert_not_called()
        _notify_mentor_of_mentored_leaving.assert_not_called()

    @patch('mail_manager.MailManager._send_confirmation_to_mentored')
    @patch('mail_manager.MailManager._send_confirmation_to_mentor')
    @patch('mail_manager.MailManager._notify_subscribed_users_not_selected')
    @patch('mail_manager.MailManager._notify_subscribed_users_of_mentoring_canceled')
    @patch('mail_manager.MailManager._notify_mentor_of_mentored_leaving')
    def test_send_mail_notify_subscribed_users_not_selected(
            self, _notify_mentor_of_mentored_leaving, _notify_subscribed_users_of_mentoring_canceled,
            _notify_subscribed_users_not_selected, _send_confirmation_to_mentor, _send_confirmation_to_mentored):
        template = Template.NOTIFY_SUBSCRIBED_USERS_NOT_SELECTED
        self.mail_manager.send_mail(self.to, self.metadata, template)
        _send_confirmation_to_mentored.assert_not_called()
        _send_confirmation_to_mentor.assert_not_called()
        _notify_subscribed_users_not_selected.assert_called_once_with(self.to, self.metadata)
        _notify_subscribed_users_of_mentoring_canceled.assert_not_called()
        _notify_mentor_of_mentored_leaving.assert_not_called()

    @patch('mail_manager.MailManager._send_confirmation_to_mentored')
    @patch('mail_manager.MailManager._send_confirmation_to_mentor')
    @patch('mail_manager.MailManager._notify_subscribed_users_not_selected')
    @patch('mail_manager.MailManager._notify_subscribed_users_of_mentoring_canceled')
    @patch('mail_manager.MailManager._notify_mentor_of_mentored_leaving')
    def test_send_mail_notify_subscribed_users_of_mentoring_canceled(
            self, _notify_mentor_of_mentored_leaving, _notify_subscribed_users_of_mentoring_canceled,
            _notify_subscribed_users_not_selected, _send_confirmation_to_mentor, _send_confirmation_to_mentored):
        template = Template.NOTIFY_SUBSCRIBED_USERS_MENTORING_CANCELED
        self.mail_manager.send_mail(self.to, self.metadata, template)
        _send_confirmation_to_mentored.assert_not_called()
        _send_confirmation_to_mentor.assert_not_called()
        _notify_subscribed_users_not_selected.assert_not_called()
        _notify_subscribed_users_of_mentoring_canceled.assert_called_once_with(self.to, self.metadata)
        _notify_mentor_of_mentored_leaving.assert_not_called()

    @patch('mail_manager.MailManager._send_confirmation_to_mentored')
    @patch('mail_manager.MailManager._send_confirmation_to_mentor')
    @patch('mail_manager.MailManager._notify_subscribed_users_not_selected')
    @patch('mail_manager.MailManager._notify_subscribed_users_of_mentoring_canceled')
    @patch('mail_manager.MailManager._notify_mentor_of_mentored_leaving')
    def test_send_mail_notify_mentor_of_mentored_leaving(
            self, _notify_mentor_of_mentored_leaving, _notify_subscribed_users_of_mentoring_canceled,
            _notify_subscribed_users_not_selected, _send_confirmation_to_mentor, _send_confirmation_to_mentored):
        template = Template.NOTIFY_MENTOR_OF_MENTORED_LEAVING
        self.mail_manager.send_mail(self.to, self.metadata, template)
        _send_confirmation_to_mentored.assert_not_called()
        _send_confirmation_to_mentor.assert_not_called()
        _notify_subscribed_users_not_selected.assert_not_called()
        _notify_subscribed_users_of_mentoring_canceled.assert_not_called()
        _notify_mentor_of_mentored_leaving.assert_called_once_with(self.to, self.metadata)


if __name__ == '__main__':
    unittest.main()
