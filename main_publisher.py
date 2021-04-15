import argparse
import json
import random
from os import environ

import pika

from producer.producer import Producer
from queue_manager import QueueManager

if __name__ == '__main__':
    QUEUE_SERVICE_URL = environ.get('QUEUE_SERVICE_URL', 'amqp://guest:guest@localhost:5672/%2f')

    queue_manager = QueueManager(QUEUE_SERVICE_URL)

    channel = queue_manager.channel()
    channel.queue_declare(queue=QueueManager.QUEUE_NAME, arguments={'x-max-priority': 255})

    parser = argparse.ArgumentParser('main_publisher')
    parser.add_argument('-n', dest='number_of_messages', default=1, help='The number of messages to generate', type=int)
    args = parser.parse_args()

    producer = Producer()
    for i in range(0, args.number_of_messages):
        template = random.randint(1, 5)
        if template == 1:
            payload = producer.produce_confirmation_to_mentor()
        elif template == 2:
            payload = producer.produce_confirmation_to_mentored()
        elif template == 3:
            payload = producer.produce_notify_mentor_of_mentored_leaving()
        elif template == 4:
            payload = producer.produce_notify_subscribed_users_not_selected()
        else:
            payload = producer.produce_notify_subscribed_users_of_mentoring_canceled()
        channel.basic_publish(exchange='', routing_key=QueueManager.QUEUE_NAME, body=json.dumps(payload.dict(),
                                                                                                default=str),
                              properties=pika.BasicProperties(priority=payload.get_priority_value()))
        print(f'Message with priority {payload.get_priority_value()} and template {payload.template} sent!')

    queue_manager.close()
