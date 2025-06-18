import joblib  # Để lưu mô hình chuẩn hóa
import pandas as pd
from pytorch_tabnet.tab_model import TabNetClassifier
import numpy as np

class TabnetPrediction:

    def __init__(self, *args, **kwargs):
        self.selected_columns = ['Flow Duration', 'Total Fwd Packets',
                    'Total Backward Packets', 'Fwd Packets Length Total',
                    'Bwd Packets Length Total', 'Fwd Packet Length Max',
                    'Fwd Packet Length Min', 'Fwd Packet Length Mean',
                    'Fwd Packet Length Std', 'Bwd Packet Length Max',
                    'Bwd Packet Length Min', 'Bwd Packet Length Mean',
                    'Bwd Packet Length Std', 'Flow Bytes/s', 'Flow Packets/s',
                    'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
                    'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max',
                    'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std',
                    'Bwd IAT Max', 'Bwd IAT Min',  'Fwd Header Length',
                    'Bwd Header Length', 'Fwd Packets/s', 'Bwd Packets/s',
                    'Packet Length Min', 'Packet Length Max', 'Packet Length Mean',
                    'Packet Length Std', 'Packet Length Variance', 
                    'Down/Up Ratio',
                    'Avg Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
                    'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
                        'Subflow Fwd Bytes', 'Subflow Bwd Packets',
                    'Subflow Bwd Bytes', 'Init Fwd Win Bytes', 'Init Bwd Win Bytes',
                    'Fwd Act Data Packets', 'Fwd Seg Size Min', 'Active Mean', 'Active Std',
                    'Active Max', 'Active Min', 'Label']
        
        self.model = TabNetClassifier()
        self.model.load_model("models/tabnet/tabnet.zip")
        self.scaler = joblib.load("models/tabnet/scaler.pkl")
        self.selector = joblib.load("models/tabnet/selector.pkl")
        self.labels = ['BENIGN', 'Group1', 'Group2', 'Syn']

    def predict(self, chunk):
        row = chunk[self.selected_columns].copy()
        X = row.drop(columns=['Label'])
        X.fillna(X.median(), inplace=True)

        X_scaled = self.scaler.transform(X)
        X_selected = self.selector.transform(X_scaled)
        
        # xac suat du doan cua cac lop
        y_proba = self.model.predict_proba(X_selected)
        
        # nhan du doan
        y_pred = np.argmax(y_proba, axis=1)
        predicted_label = self.labels[int(y_pred[0])]
        
        # Lấy độ tin cậy (xác suất cao nhất)
        confidence_score = np.max(y_proba, axis=1)[0]
        
        return {
            "predicted_label": predicted_label,
            "confidence_score": float(confidence_score),
            # "class_probabilities": dict(zip(self.labels, y_proba[0].tolist()))
        }
        