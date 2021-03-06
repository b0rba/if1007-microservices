from os import environ

import prometheus_client
from apscheduler.schedulers.background import BlockingScheduler

from consumer.consumer import Consumer
from mail_manager import MailManager


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    prometheus_client.start_http_server(5000)

    SENDINBLUE_URL = environ.get('SENDINBLUE_URL', 'https://api.sendinblue.com/v3')
    SENDINBLUE_API_KEY = environ.get('SENDINBLUE_API_KEY', '')
    SENDINBLUE_MAILS_PER_HOUR = int(environ.get('SENDINBLUE_MAILS_PER_HOUR', 12))
    QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@rabbitmq:5672/%2f')

    mail_manager = MailManager(SENDINBLUE_API_KEY, SENDINBLUE_URL)

    consumer = Consumer(mail_manager, SENDINBLUE_MAILS_PER_HOUR, QUEUE_SERVICE_URL)

    scheduler.add_job(consumer.consume_mails_per_hour, 'cron',
                      year='*', month='*', day='*', week='*', day_of_week='*', hour='*', minute=0, second=0,
                      id='mails-every-hour')
    scheduler.add_job(consumer.consume_send_last_mails, 'cron',
                      year='*', month='*', day='*', week='*', day_of_week='*', hour=23, minute=5, second=0,
                      id='last-mails')
    print('Application started!')
    scheduler.start()
