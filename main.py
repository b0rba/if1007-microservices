from os import environ

from mail_manager import MailManager

if __name__ == '__main__':
    SENDINBLUE_URL = environ.get('SENDINBLUE_URL', 'https://api.sendinblue.com/v3/smtp/email')
    SENDINBLUE_API_KEY = environ.get('SENDINBLUE_API_KEY', '')
    mail_manager = MailManager(SENDINBLUE_API_KEY, SENDINBLUE_URL)
