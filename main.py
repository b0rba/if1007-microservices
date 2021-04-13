from os import environ

from pika import spec
from pika.adapters.blocking_connection import BlockingChannel

from mail_manager import MailManager
from queue_manager import QueueManager

if __name__ == '__main__':
    SENDINBLUE_URL = environ.get('SENDINBLUE_URL', 'https://api.sendinblue.com/v3/smtp/email')
    SENDINBLUE_API_KEY = environ.get('SENDINBLUE_API_KEY', '')
    mail_manager = MailManager(SENDINBLUE_API_KEY, SENDINBLUE_URL)

    QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@localhost:5672/%2f')

    queue_manager = QueueManager(QUEUE_SERVICE_URL)

    channel = queue_manager.channel()
    channel.queue_declare(queue=QueueManager.QUEUE_NAME)

    def dummy_consumer(msg: bytes):
        print(msg.decode())

    def callback(_: BlockingChannel, method: spec.Basic.Deliver, properties: spec.BasicProperties, body):
        dummy_consumer(body)

    channel.basic_consume(QueueManager.QUEUE_NAME, callback, auto_ack=True)
    channel.start_consuming()

    queue_manager.close()
