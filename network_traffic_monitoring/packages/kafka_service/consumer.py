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
                data_x = DataFrame([message_dict])

                label_index = predict(self.model , data_x)
                labels = ['BENIGN', 'LDAP', 'MSSQL', 'NetBIOS', 'Portmap', 'Syn', 'UDP', 'UDPLag']
                print(labels[label_index])
                message_dict['predict'] = 'labels[label_index]'

                url = "http://371d-2401-d800-bab0-c299-d0f0-b9f8-c911-82a0.ngrok-free.app"  # API giả lập
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "data": message_dict
                }

                # print('predict:', message_dict['predict'])
                
                response = session.post(url + '/tracking/send', json=payload, headers=headers, verify=False)

                if response.status_code == 200 or response.status_code == 201:  # Kiểm tra nếu request thành công
                    # data = response.json()  # Chuyển đổi dữ liệu JSON thành dict
                    # print(data)
                    print("gui thanh cong")
                    pass
                else:
                    print(f"Lỗi {response.status_code}")
                
                