import os
import numpy as np
import pandas as pd
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
from flask import Flask, request, jsonify
from sklearn.preprocessing import MinMaxScaler
import random
import io
import joblib

# Load pre-trained ResNet50 model
MODEL_PATH = "resnet50_finetuned.pth"
SCALER_PATH = "scaler.pkl"
GRID_POSITIONS_PATH = "grid_positions.npy"

model = models.resnet50(pretrained=False)
model.fc = torch.nn.Linear(model.fc.in_features, 4)  # 4 lớp output
model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
model.eval()

# Load precomputed MinMaxScaler and grid positions
scaler = joblib.load(SCALER_PATH)
grid_positions = np.load(GRID_POSITIONS_PATH)

# Define image transformations
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
])

# Selected columns (same as in data preprocessing)
selected_columns = ['Protocol', 'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets', 
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

def prepare_data(data: pd.DataFrame):
    data = data[selected_columns]
    data.replace([-np.inf, np.inf], 0, inplace=True)
    data.fillna(0, inplace=True)
    
    data = np.log1p(data + 1)
    data.replace([-np.inf, np.inf], 0, inplace=True)
    data.fillna(0, inplace=True)
    
    features = scaler.transform(data.values)  # Use precomputed scaler
    return features

def process_row_to_image(row, grid_positions, grid_size=7, image_size=224):
    grid = np.zeros((grid_size, grid_size), dtype=float)
    count = np.zeros((grid_size, grid_size), dtype=int)
    
    for i in range(len(row)):
        x, y = grid_positions[i]
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

def predict(image):
    image = transform(image).unsqueeze(0)
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
    return predicted.item()

# Flask API
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict_api():
    data = request.get_json()
    df = pd.DataFrame([data])
    features = prepare_data(df)
    image = process_row_to_image(features[0], grid_positions)
    label = predict(image)
    return jsonify({"label": label})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
