from prometheus_client import Counter

MAILS_SENT = Counter(name='mails_sent', documentation='Mails Send It')
MAILS_FAIL = Counter(name='mails_fails', documentation='Mails Failed')

QUEUE_CONSUMER_BY_TEMPLATE = Counter(name='payload_template', documentation='Queue Consumer by value of template',
                                     labelnames=['template'])
QUEUE_CONSUMER_BY_PRIORITY = Counter(name='payload_priority', documentation='Queue Consumer by priority',
                                     labelnames=['priority'])
