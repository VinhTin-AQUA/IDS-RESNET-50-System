


datadir = 'test'
def convert(df_normalized_splited, label, num):
    # Kích thước ảnh ban đầu (5x15) => Mở rộng mỗi điểm thành 3x3 pixel => Ảnh mới (15x45)
    image_size = (8, 8) # kích thước ảnh ban đầu
    upscale_factor = 28 # tỉ lệ tăng kích thước điểm ảnh => size ảnh: (8x28) x (8x28)
    new_image_size = (image_size[0] * upscale_factor, image_size[1] * upscale_factor)

    os.makedirs(f"data/{datadir}/{label}", exist_ok=True)  # Tạo thư mục nếu chưa có

    i = 1
    for row in df_normalized_splited.values:
        '''code'''

        '''
        chỉ làm mờ: 0.3, không mờ 0,7 ==> 0.21 xác xuất chỉ mờ
        chỉ làm nhiễu: 0.3, không nhiễu 0,7 ==> 0.21 xác xuất chỉ nhiễu
        vừa mờ: 0.3, vừa nhiễu 0.3 ==> xác xuất vừa mờ vừa nhiễu: 0.09
        không mờ: 0.7, không nhiễu: 0.7 ==> xác xuất không mờ không nhiễu: 0.49
        '''

        # Xác suất ngẫu nhiên để thêm hiệu ứng (30% ảnh bị làm mờ, 30% ảnh bị nhiễu)
        blur_prob = random.random() < 0.3  # 30% xác suất làm mờ
        noise_prob = random.random() < 0.3  # 30% xác suất thêm nhiễu

        # làm mờ ảnh
        if blur_prob < 0.3:
            image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(1, 5))) # mức độ mờ từ 1 đến 5



        
        #làm nhiễu ảnh
        if noise_prob < 1:

            '''
            np.random.normal(mean, std, size)
                mean=0, +20 Ảnh trở nên sáng hơn, vì tất cả pixel đều bị cộng thêm giá trị trung bình 20, -20 Ảnh trở nên tối hơn, vì tất cả pixel bị trừ đi 20
                std = 25, 10 Nhiễu nhẹ, ảnh vẫn rất rõ ràng, 25 (mặc định) Nhiễu trung bình, ảnh có độ biến động nhưng vẫn nhận diện được, 50 Nhiễu mạnh, ảnh bị méo đáng kể, 100 Nhiễu cực mạnh, ảnh có thể bị phá hủy hoàn toàn
                size=(new_image_size[0], new_image_size[1]): Kích thước của ma trận nhiễu bằng với kích thước ảnh.
            '''
            noise = np.random.normal(0, 25, (new_image_size[0], new_image_size[1]))  # Thêm nhiễu Gaussian

            '''
            image.convert("L"): Chuyển ảnh từ RGB sang grayscale trước khi thêm nhiễu. Điều này giúp nhiễu dễ xử lý hơn và đảm bảo nhiễu ảnh hưởng đồng đều lên tất cả các kênh màu.
            np.array(image.convert("L")): Chuyển ảnh grayscale thành mảng numpy chứa giá trị pixel (0-255).
            + noise: Cộng ma trận nhiễu vào từng pixel của ảnh.
            '''
            noisy_image_array = np.array(image.convert("L")) + noise  # Chuyển sang grayscale trước khi thêm nhiễu

            
            '''
            np.clip(array, 0, 255): Đảm bảo giá trị pixel nằm trong khoảng hợp lệ từ 0 đến 255, <0 thì lấy 0, >255 thì lấy 255
            .astype(np.uint8): Chuyển kiểu dữ liệu thành uint8 (số nguyên 8-bit), vì ảnh cần được lưu trữ trong dạng 8-bit grayscale hoặc RGB.
            '''
            noisy_image_array = np.clip(noisy_image_array, 0, 255).astype(np.uint8)  # Giữ giá trị trong khoảng 0-255
            image = Image.fromarray(noisy_image_array).convert("RGB")
            

        '''code'''