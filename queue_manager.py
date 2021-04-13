import pika


class QueueManager:
    def __init__(self, url: str):
        params = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(params)

    def channel(self):
        return self.connection.channel()

    def close(self):
        self.connection.close()
