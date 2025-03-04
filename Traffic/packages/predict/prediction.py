import torch
import numpy as np
import pandas as pd
import json
import cv2
from torchvision import transforms, models
from PIL import Image
import torchvision.transforms.functional as F

selected_columns = ['tot_fwd_pkts','tot_bwd_pkts','totlen_fwd_pkts','totlen_bwd_pkts',
 'fwd_pkt_len_max','fwd_pkt_len_min','fwd_pkt_len_mean','fwd_pkt_len_std',
 'bwd_pkt_len_max','bwd_pkt_len_min','bwd_pkt_len_mean','bwd_pkt_len_std',
 'flow_byts_s','flow_pkts_s','flow_iat_mean','flow_iat_std','flow_iat_max',
 'flow_iat_min','fwd_iat_tot','fwd_iat_mean','fwd_iat_std','fwd_iat_max',
 'fwd_iat_min','bwd_iat_tot','bwd_iat_mean','bwd_iat_std','bwd_iat_max',
 'bwd_iat_min','fwd_psh_flags','bwd_psh_flags','fwd_urg_flags','bwd_urg_flags',
 'fwd_header_len','bwd_header_len','pkt_len_min','pkt_len_max','pkt_len_mean',
 'pkt_len_std','pkt_len_var','pkt_size_avg','fwd_seg_size_avg','bwd_seg_size_avg',
 'fwd_byts_b_avg','fwd_pkts_b_avg','bwd_byts_b_avg','bwd_pkts_b_avg',
 'subflow_fwd_pkts','subflow_fwd_byts','subflow_bwd_pkts','subflow_bwd_byts',
 'init_fwd_win_byts','init_bwd_win_byts','fwd_act_data_pkts','fwd_seg_size_min',
 'active_mean','active_std','active_max','active_min','idle_mean','idle_std',
 'idle_max','idle_min','cwr_flag_cnt','ece_flag_cnt',]


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
    df_real_time = df_real_time.copy()
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
    # """ Chuyển vector dữ liệu thành ảnh grayscale 224x224 """
    # img_array = data.to_numpy().reshape((img_size, img_size))  # Giả sử dữ liệu đã có kích thước phù hợp
    
    # # Chuẩn hóa về 0-255
    # img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)
    
    # # Chuyển thành ảnh màu (3 kênh)
    # img = cv2.merge([img_array, img_array, img_array])  # ResNet50 cần 3 kênh RGB
    
    image_size = (8, 8)
    upscale_factor = 28

    # Chuyển đổi dòng thành ma trận ảnh ban đầu (8x8)
    image_array = np.array(data.values[0]).reshape(image_size)
    image_array = np.nan_to_num(image_array, nan=0.0, posinf=1.0, neginf=0.0)  # Thay thế giá trị NaN bằng 0
    # image_array = np.clip(image_array, 0, 1) # Giới hạn trong khoảng hợp lệ

    # Phóng to mỗi pixel np.kron()
    upscale_matrix = np.ones((upscale_factor, upscale_factor))
    enlarged_image_array = np.kron(image_array, upscale_matrix)

    # Chuyển đổi sang ảnh
    image = Image.fromarray((enlarged_image_array * 255).astype(np.uint8))  # Chuyển sang RGB
    image = image.convert("RGB")
    
    return image

# ==== 5. Load Model đã Train ====
def load_model(model_path="models/resnet50_finetuned.pth", num_classes=8):
    """ Load mô hình ResNet50 đã train """
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)  # Chỉnh số lớp đầu ra
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()  # Chế độ đánh giá (không training)
    return model


# ==== 6. Tiền xử lý ảnh và dự đoán ====
def predict(model, data):
    data = data[selected_columns]

    # predict
    min, max = load_train_stats()
    data_normalized = preprocess_real_time_data(data, min, max)
    img = data_to_image(data_normalized)

    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device("cpu")

    """ Dự đoán nhãn của ảnh đầu vào """
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((224, 224)),  
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    if isinstance(img, Image.Image):  # Nếu img là PIL Image, chuyển sang Tensor
        img = F.to_tensor(img)

    img_tensor = transform(img).unsqueeze(0).to(device)  # Thêm batch dimension
    
    with torch.no_grad():
        output = model(img_tensor)
    
    predicted_class = torch.argmax(output, dim=1).item()
    
    return predicted_class

