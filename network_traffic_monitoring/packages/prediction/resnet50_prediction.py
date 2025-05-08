from torchvision import transforms, models
import torch
import joblib  # Để lưu mô hình chuẩn hóa
import pandas as pd
import numpy as np
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

        self.tab2Img = joblib.load("scaler/tab2img.pkl")
        self.transform = transforms.Compose([
                        transforms.Resize((224, 224)),
                        transforms.ToTensor(),
                        transforms.Normalize([0.485, 0.456, 0.406],
                                            [0.229, 0.224, 0.225])])
    
        self.label_map = ['BENIGN', 'Group1', 'Group2', 'Syn']
        self.num_classes = len(self.label_map)

        self.device = torch.device("cpu")
        self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

        for name, param in self.model.named_parameters():
            if 'layer3' in name or 'layer4' in name or 'fc' in name:
                param.requires_grad = True
            else:
                param.requires_grad = False

        self.model.fc = nn.Sequential(
            nn.Linear(self.model.fc.in_features, 1024),  # Tăng số neuron
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(0.3),  
            nn.Linear(1024, 512),
            nn.GELU(), 
            nn.Linear(512, self.num_classes)
        )
        self.model = self.model.to(self.device)
        self.model.load_state_dict(torch.load("models/resnet50_finetuned.pth",  map_location=self.device))
        self.model.eval()

    def predict(self, data: pd.DataFrame):
        data = data[self.selected_columns]
        row = data.to_numpy() 

        img_array = self.tab2Img.transform(row.reshape(1, -1))[0] 
        org_size = 7
        img_size = 224
        scale_factor = img_size // org_size
        
        # Reshape và chuẩn hóa
        img_array = img_array.reshape(org_size, org_size)
        if img_array.max() <= 1.0:
            img_array = (img_array * 255).astype(np.uint8)
        else:
            img_array = img_array.astype(np.uint8)
        
        zoomed_array = np.kron(img_array, np.ones((scale_factor, scale_factor)))
        scaled_image = zoomed_array.astype(np.uint8)
        img = Image.fromarray(scaled_image, mode='L').convert("RGB")
        input_tensor = self.transform(img).unsqueeze(0).to(self.device)  # Thêm batch dimension

        with torch.no_grad():
            output = self.model(input_tensor)
            predicted_class = torch.argmax(output, dim=1).item()
        # print(predicted_class)
        return self.label_map[predicted_class]
        