from confluent_kafka import Consumer
from packages.kafka_service.kafka_config import KAFKA_CONFIG, TOPIC_NAME
import json
import requests
from pandas.core.frame import DataFrame
from ..prediction.resnet50_prediction import Resnet50Prediction
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # loai bo canh bao goi api co SSL khong hop le


class KafkaConsumer:
   
    def __init__(self):
        self.consumer = Consumer(KAFKA_CONFIG)
        self.consumer.subscribe([TOPIC_NAME])
        self.model = Resnet50Prediction()

    def consume_messages(self):
        session = requests.Session()

        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'Error: {msg.error()}')
            else:
                message_dict = json.loads(msg.value().decode('utf-8'))
                df = DataFrame([message_dict])
                predict_label = self.model.predict(df)
                message_dict['Predict'] = predict_label

                print(message_dict['Predict'])
                
                url = "http://bf81-113-161-36-23.ngrok-free.app"  # API giả lập
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "data": message_dict
                }

                response = session.post(url + '/tracking/send', json=payload, headers=headers, verify=False)

                if response.status_code == 200 or response.status_code == 201:  # Kiểm tra nếu request thành công
                    # data = response.json()  # Chuyển đổi dữ liệu JSON thành dict
                    # print(data)
                    print("gui thanh cong")
                    pass
                else:
                    print(f"Lỗi {response.status_code}")
                
                
