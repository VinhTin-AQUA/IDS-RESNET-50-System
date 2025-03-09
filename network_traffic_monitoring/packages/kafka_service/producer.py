from confluent_kafka import Producer
from packages.kafka_service.kafka_config import KAFKA_CONFIG, TOPIC_NAME

class KafkaProducer:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KafkaProducer, cls).__new__(cls)
            cls._instance.producer = Producer({
                'bootstrap.servers': KAFKA_CONFIG['bootstrap.servers'],
                # 'queue.buffering.max.ms': 1  # Gửi ngay lập tức thay vì chờ buffer đầy
            })
        return cls._instance

    def send_message(self, key, value):
        self.producer.produce(TOPIC_NAME, key=key, value=value, callback=self.delivery_report)
        self.producer.flush()  # Đảm bảo gửi hết tin nhắn


    def delivery_report(self, err, msg):
        if err:
            print(f'Error: {err}')
        # else:
            # print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
            



