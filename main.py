from os import environ

from mail_manager import MailManager
from queue_manager import QueueManager

if __name__ == '__main__':
    SENDINBLUE_URL = environ.get('SENDINBLUE_URL', 'https://api.sendinblue.com/v3/smtp/email')
    SENDINBLUE_API_KEY = environ.get('SENDINBLUE_API_KEY', '')
    mail_manager = MailManager(SENDINBLUE_API_KEY, SENDINBLUE_URL)

    QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@localhost:5672/%2f')

    queue_manager = QueueManager(QUEUE_SERVICE_URL)

    channel = queue_manager.channel()
    channel.queue_declare(queue='test')
    channel.start_consuming()
    channel.close()

    queue_manager.close()
