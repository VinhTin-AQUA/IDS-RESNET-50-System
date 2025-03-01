import torch
import numpy as np
import pandas as pd
import json
import cv2
from torchvision import transforms, models
from PIL import Image


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
    data_features = np.log1p(df_real_time.clip(lower=0))
    
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
def load_model(model_path="model.pth", num_classes=10):
    """ Load mô hình ResNet50 đã train """
    model = models.resnet50()
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)  # Chỉnh số lớp đầu ra
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()  # Chế độ đánh giá (không training)
    return model


# ==== 6. Tiền xử lý ảnh và dự đoán ====
def predict(model, img):




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

