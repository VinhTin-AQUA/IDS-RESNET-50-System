from confluent_kafka import Consumer
from packages.kafka_service.kafka_config import KAFKA_CONFIG, TOPIC_NAME
import json

class KafkaConsumer:
    def __init__(self):
        self.consumer = Consumer(KAFKA_CONFIG)
        self.consumer.subscribe([TOPIC_NAME])

    def consume_messages(self):
        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'Error: {msg.error()}')
            else:
                message_dict = json.loads(msg.value().decode('utf-8'))
                
