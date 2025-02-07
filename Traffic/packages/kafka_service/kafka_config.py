KAFKA_CONFIG = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'data-flow',
    'auto.offset.reset': 'earliest'  # Đọc từ đầu topic
}

TOPIC_NAME = 'get-data-flow'
