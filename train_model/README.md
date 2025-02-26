

### Datasets

CIC DDOS 2018
https://www.kaggle.com/datasets/solarmainframe/ids-intrusion-csv?select=03-02-2018.csv


CIC DDOS 2019 full dataset
https://www.kaggle.com/datasets/rodrigorosasilva/cic-ddos2019-30gb-full-dataset-csv-files


BoTNeTIoT-L01-v2
https://www.kaggle.com/datasets/azalhowaide/iot-dataset-for-intrusion-detection-systems-ids?select=BoTNeTIoT-L01-v2.csv


RT-IoT2022
https://www.kaggle.com/datasets/joebeachcapital/real-time-internet-of-things-rt-iot2022




### Run Pytorch with GPU

CUDA Version	Lệnh cài đặt PyTorch (pip)

12.1			pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
11.8			pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


** tạo môi trường ảo .venv

** cài đặt thư viện
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

** kiểm tra
import torch

print("Có GPU không? :", torch.cuda.is_available())  # Phải trả về True
print("Số GPU:", torch.cuda.device_count())  # Phải lớn hơn 0
print("Tên GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "Không có GPU")
print("Phiên bản CUDA trong PyTorch:", torch.version.cuda)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Đang sử dụng: {device}") # phải là: Đang sử dụng: cuda
