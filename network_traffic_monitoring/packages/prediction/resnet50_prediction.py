from torchvision import transforms, models
import torch
import joblib  # Để lưu mô hình chuẩn hóa
from pandas.core.frame import DataFrame
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import RobustScaler, MinMaxScaler, StandardScaler
from PIL import Image
import torchvision.transforms.functional as F
import torch.nn as nn

class Resnet50Prediction:

    def __init__(self, *args, **kwargs):
        
        (self.mean, self.std) = self.load_train_stats()
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")
        self.labels = ['BENIGN', 'LDAP', 'MSSQL', 'Portmap', 'Syn', 'UDP', 'UDPLag']
        self.selected_columns = ['Total Fwd Packets', 'Total Backward Packets',
                                'Fwd Packets Length Total', 'Bwd Packets Length Total',
                                'Fwd Packet Length Max', 'Fwd Packet Length Min',
                                'Fwd Packet Length Mean', 'Fwd Packet Length Std',
                                'Bwd Packet Length Max', 'Bwd Packet Length Min',
                                'Bwd Packet Length Mean', 'Bwd Packet Length Std', 'Flow Bytes/s',
                                'Flow Packets/s', 'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max',
                                'Flow IAT Min', 'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std',
                                'Fwd IAT Max', 'Fwd IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean',
                                'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min', 'Fwd PSH Flags',
                                'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length',
                                'Bwd Header Length',
                                'Packet Length Min', 'Packet Length Max', 'Packet Length Mean',
                                'Packet Length Std', 'Packet Length Variance', 
                                'CWE Flag Count', 'ECE Flag Count',
                                'Avg Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
                                'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 
                                'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 
                                'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets',
                                'Subflow Bwd Bytes', 'Init Fwd Win Bytes', 'Init Bwd Win Bytes',
                                'Fwd Act Data Packets', 'Fwd Seg Size Min', 'Active Mean', 'Active Std',
                                'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max',
                                'Idle Min',]
        self.model = self.load_model()

    def load_model(self):
        model_path = 'models/resnet50_finetuned.pth'

        """ Load ResNet50 model """
        model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(self.labels))  # Adjust output layer
        model = model.to(self.device)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        return model

    def load_train_stats(self):
        ## Load min và max từ file
        with open("scaler/train_min_max.json", "r") as f:
            data = json.load(f)

        mean = pd.Series(data["mean"])
        std = pd.Series(data["std"])
        return mean, std

    def normalize(self, df):
        data = df.copy()
        data.replace([-np.inf, np.inf], 0, inplace=True)
        data.fillna(self.mean, inplace=True)

        self.std.replace(0, 1, inplace=True) # 

        data = (data - self.mean) / self.std

        data.fillna(0, inplace=True)

        data_df = np.log1p(data + 1)
        data_scaled = pd.DataFrame(MinMaxScaler(feature_range=(0, 255)).fit_transform(data_df).astype(np.uint8))

        return data_scaled

    def data_to_image(self, data):
        image_size = (8, 8)
        upscale_factor = 28

        for row in data.values:
            # Chuyển đổi dòng thành ma trận ảnh ban đầu (8x8)
            image_array = np.array(row).reshape(image_size)
            image_array = np.nan_to_num(image_array, nan=0.0, posinf=1.0, neginf=0.0)  # Thay thế giá trị NaN bằng 0

            # Phóng to mỗi pixel np.kron()
            upscale_matrix = np.ones((upscale_factor, upscale_factor))
            enlarged_image_array = np.kron(image_array, upscale_matrix)

            # Chuyển đổi sang ảnh
            image = Image.fromarray((enlarged_image_array * 255).astype(np.uint8))  # Chuyển sang RGB
            image = image.convert("RGB")

            # image.save('data/test/haa/r2.png')
        
        return image

    def predict(self, df):
        data = df[self.selected_columns]
        data_normalize = self.normalize(data)
        img = self.data_to_image(data_normalize)

        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),  
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        if isinstance(img, Image.Image):  # If img is PIL Image, convert to Tensor
            img = F.to_tensor(img)
       
        img_tensor = transform(img).unsqueeze(0).to(self.device)
        img_tensor = transform(img).unsqueeze(0)
        with torch.no_grad():
            output = self.model(img_tensor)
        predicted_class = torch.argmax(output, dim=1).item()

        return self.labels[predicted_class]