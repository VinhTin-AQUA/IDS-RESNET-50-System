import torch
import numpy as np
import pandas as pd
import json
import cv2
from torchvision import transforms, models
from PIL import Image


selected_columns = ['Total Fwd Packets', 'Total Backward Packets',
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

       'Avg Packet Size', 'Avg Fwd Segment Size', 'Avg Bwd Segment Size',
       'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate',
       'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate',
       'Subflow Fwd Packets', 'Subflow Fwd Bytes', 'Subflow Bwd Packets',
       'Subflow Bwd Bytes', 'Init Fwd Win Bytes', 'Init Bwd Win Bytes',
       'Fwd Act Data Packets', 'Fwd Seg Size Min', 'Active Mean', 'Active Std',
       'Active Max', 'Active Min', 'Idle Mean', 'Idle Std', 'Idle Max',
       'Idle Min']

# ==== 2. Load thống kê train ====
def load_train_stats():
    ## Load min và max từ file
    with open("train_min_max.json", "r") as f:
        min_max = json.load(f)

    train_min = pd.Series(min_max["min"])
    train_max = pd.Series(min_max["max"])
    return train_min, train_max

# ==== 3. Chuẩn hóa dữ liệu ====
def preprocess_real_time_data(df_real_time, train_min, train_max):
    df_real_time.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_real_time.fillna(train_min, inplace=True)  # Thay NaN bằng min đã lưu
    
    # Log-transform
    # data_features = np.log1p(df_real_time.clip(lower=0))
    
    # Chuẩn hóa Min-Max
    data_features = np.log1p(df_real_time + 1)
    data_scaled = (data_features - train_min) / (train_max - train_min)
    return data_scaled

# ==== 4. Chuyển đổi dữ liệu thành hình ảnh ====
def data_to_image(data, img_size=224):
    """ Chuyển vector dữ liệu thành ảnh grayscale 224x224 """
    img_array = data.to_numpy().reshape((img_size, img_size))  # Giả sử dữ liệu đã có kích thước phù hợp
    
    # Chuẩn hóa về 0-255
    img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)
    
    # Chuyển thành ảnh màu (3 kênh)
    img = cv2.merge([img_array, img_array, img_array])  # ResNet50 cần 3 kênh RGB
    
    return img

# ==== 5. Load Model đã Train ====
def load_model(model_path="resnet50_finetuned.pth", num_classes=8):
    """ Load mô hình ResNet50 đã train """
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)  # Chỉnh số lớp đầu ra
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()  # Chế độ đánh giá (không training)
    return model


# ==== 6. Tiền xử lý ảnh và dự đoán ====
def predict(model, data):

    # 

    # predict
    min, max = load_train_stats()
    data_normalized = preprocess_real_time_data(data, min, max)
    img = data_to_image(data_normalized)



    """ Dự đoán nhãn của ảnh đầu vào """
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),  
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  
    ])
    
    img_tensor = transform(img).unsqueeze(0)  # Thêm batch dimension
    
    with torch.no_grad():
        output = model(img_tensor)
    
    predicted_class = torch.argmax(output, dim=1).item()
    
    return predicted_class

