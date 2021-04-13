import argparse
from os import environ

from queue_manager import QueueManager

if __name__ == '__main__':
    QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@localhost:5672/%2f')

    queue_manager = QueueManager(QUEUE_SERVICE_URL)

    channel = queue_manager.channel()
    channel.queue_declare(queue=QueueManager.QUEUE_NAME)

    parser = argparse.ArgumentParser('producer_dummy')
    parser.add_argument('-m', dest='message', default='Dummy message', help='A text to send', type=str)
    args = parser.parse_args()

    channel.basic_publish(exchange='', routing_key=QueueManager.QUEUE_NAME, body=args.message)
    print('Message sent!')
    queue_manager.close()
