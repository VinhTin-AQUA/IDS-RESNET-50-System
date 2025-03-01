from confluent_kafka import Consumer
from packages.kafka_service.kafka_config import KAFKA_CONFIG, TOPIC_NAME
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context
from pandas.core.frame import DataFrame
from packages.flow_realtime import constants
from packages.predict.prediction import load_model, predict
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # loai bo canh bao goi api co SSL khong hop le

class KafkaConsumer:
    _model_instance = None

    def __new__(cls):
        if cls._model_instance is None:
            cls._model_instance = super(KafkaConsumer, cls).__new__(cls)
            cls._model_instance.model = load_model()
        return cls._model_instance

    def __init__(self):
        self.consumer = Consumer(KAFKA_CONFIG)
        self.consumer.subscribe([TOPIC_NAME])

    def consume_messages(self):
        session = requests.Session() # duy tri 1 ket noi, neu tao qua nhieu ket noi se bi rate limiting boi ngrok 
        self.model = load_model()
        

        while True:
            msg = self.consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f'Error: {msg.error()}')
            else:
                message_dict = json.loads(msg.value().decode('utf-8'))

                # dự đoán
                data_x = DataFrame([message_dict])

                label = predict(self.model , data_x)

                print(label)
                # gửi kết quả
                url = "http://2710-113-161-36-10.ngrok-free.app"  # API giả lập
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "data": message_dict
                }
                
                response = session.post(url + '/tracking/send', json=payload, headers=headers, verify=False)

                if response.status_code == 200 or response.status_code == 201:  # Kiểm tra nếu request thành công
                    # data = response.json()  # Chuyển đổi dữ liệu JSON thành dict
                    # print(data)
                    # print("gui thanh cong")
                    pass
                else:
                    print(f"Lỗi {response.status_code}")
                # predict
                
