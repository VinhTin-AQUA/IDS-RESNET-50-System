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
        self.selected_columns = ['Protocol', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 
                    'Fwd Packets Length Total', 'Fwd Packet Length Max', 'Fwd Packet Length Min', 
                    'Fwd Packet Length Std', 'Bwd Packet Length Max', 'Bwd Packet Length Min', 
                    'Bwd Packet Length Mean', 'Flow Bytes/s', 'Flow Packets/s', 'Flow IAT Mean', 
                    'Flow IAT Max', 'Flow IAT Min', 'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Min', 
                    'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags', 'Fwd Header Length', 
                    'Bwd Header Length', 'Bwd Packets/s', 'Packet Length Max', 'FIN Flag Count', 'SYN Flag Count', 
                    'PSH Flag Count', 'ACK Flag Count', 'URG Flag Count', 'CWE Flag Count', 'ECE Flag Count', 'Down/Up Ratio', 
                    'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 
                    'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate', 'Init Fwd Win Bytes', 'Init Bwd Win Bytes', 
                    'Fwd Seg Size Min', 'Active Mean', 'Active Std', 'Active Max', 'Active Min', 'Idle Std']
        
        # Load precomputed MinMaxScaler and grid positions
        self.scaler_path = "scaler/scaler.pkl"
        self.grid_posisitions_path = "scaler/grid_positions.npy"

        self.scaler = joblib.load(self.scaler_path)
        self.grid_positions = np.load(self.grid_posisitions_path)

        # Define image transformations
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        self.label_map = ['BENIGN', 'Group1', 'Group2', 'Syn']

        # Kiểm tra thiết bị (GPU nếu có)
        # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device("cpu")
        
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        self.num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(self.num_ftrs, len(self.label_map))  # Adjust output layer
        self.model = self.model.to(self.device)
        self.model.load_state_dict(torch.load("models/resnet50_finetuned.pth",  map_location=self.device))
        self.model.eval()
    
    def prepare_data(self, dff: pd.DataFrame):
        df = dff.copy()
        df.replace([-np.inf, np.inf], 0, inplace=True)
        df.fillna(0, inplace=True)
        df = np.log1p(df + 1)
        df.replace([-np.inf, np.inf], 0, inplace=True)
        df.fillna(0, inplace=True)
        features = self.scaler.transform(df.values)  # Chuẩn hóa bằng scaler đã huấn luyện
        return features
    
    def process_row_to_image(self, row, grid_size=7, image_size=224):
        grid = np.zeros((grid_size, grid_size), dtype=float)
        count = np.zeros((grid_size, grid_size), dtype=int)
        
        for i in range(len(row)):
            x, y = self.grid_positions[i]
            grid[x, y] += row[i]
            count[x, y] += 1
        
        nonzero = count > 0
        grid[nonzero] = grid[nonzero] / count[nonzero]
        grid_norm = ((grid - grid.min()) / (grid.max() - grid.min() + 1e-8)) * 255
        
        upscale_factor = image_size // grid_size
        expanded_image = np.kron(grid_norm, np.ones((upscale_factor, upscale_factor)))
        img = Image.fromarray(expanded_image.astype(np.uint8), mode='L').convert("RGB")
        img = img.resize((image_size, image_size))
        return img
    
    def predict(self, df: pd.DataFrame):
        row_df = df[self.selected_columns]
        features = self.prepare_data(row_df)  # Đưa vào dạng array
        image = self.process_row_to_image(features[0])  # Chuyển thành ảnh

        # Áp dụng transform để phù hợp với mô hình
        input_tensor = self.transform(image).unsqueeze(0)  # Thêm batch dimension
        
        with torch.no_grad():
            output = self.model(input_tensor)
        predicted_class = torch.argmax(output, dim=1).item()
        return self.label_map[predicted_class]
        