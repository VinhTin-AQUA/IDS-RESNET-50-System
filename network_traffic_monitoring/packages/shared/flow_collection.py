import requests
from pandas.core.frame import DataFrame
import json
from ..prediction.tabnet_prediction import TabNetClassifier
from packages.shared.shared_data import SharedApi
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FlowCollection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FlowCollection, cls).__new__(cls)
            cls._instance._queue = []     # Mảng chứa các đối tượng
            cls._instance._size = 0       # Số lượng đối tượng
            cls._model = TabNetClassifier()
            cls._share_api = SharedApi()
        return cls._instance

    @property
    def size(self):
        return self._size

    def add(self, item):
        if (self._size > 10):
            return
        self._queue.append(item)
        self._size += 1

    def get(self):
        if self._size == 0:
            return None
        item = self._queue.pop(0)
        self._size -= 1
        return item

    def predict(self):
        session = requests.Session()
        i = 1

        while True:
            while self._size > 0:
                msg = self.get()
                message_dict = json.loads(msg.decode('utf-8'))
                df = DataFrame([message_dict])

                predict_label = self._model.predict(df)
                message_dict['Predict'] = predict_label

                print(f"{i} : {message_dict['Predict']}")
                i += 1
                
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "data": message_dict
                }

                response = session.post(self._share_api.api_base + '/tracking/flow-tracking', json=payload, headers=headers, verify=False)

                if response.status_code == 200 or response.status_code == 201:  # Kiểm tra nếu request thành công
                    data = response.json()  # Chuyển đổi dữ liệu JSON thành dict
                    print(data)
                    # print("gui thanh cong")
                    pass
                else:
                    print(f"Lỗi {response.status_code}")

    # def __str__(self):
    #     return f"Queue({self._queue}) - Size: {self._size}"
