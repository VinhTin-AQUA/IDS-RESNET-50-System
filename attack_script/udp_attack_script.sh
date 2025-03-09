#!/bin/bash

# Bắt Ctrl + C để dừng script
trap "echo -e '\nĐã dừng script!'; exit 0" SIGINT
TARGET_IP="192.168.200.60"

while true; do
    SIZE=$((RANDOM % 1701 + 300))  # Sinh số ngẫu nhiên từ 300 đến 2000
    #echo "Gửi gói UDP với kích thước $SIZE bytes"
    sudo hping3 --udp -p 80 --data $SIZE -c 1 $TARGET_IP 
        sleep 1 # chờ 1 giây trước khi gửi gói tiếp theo
    done


#!/bin/bash
# Bắt Ctrl + C để dừng script
trap "echo -e '\nĐã dừng script!'; exit 0" SIGINT

while true; do
    SIZE=$((RANDOM % 1701 + 300))  # Sinh số ngẫu nhiên từ 300 đến 2000
    #echo "Gửi gói UDP với kích thước $SIZE bytes"
    sudo hping3 --udp -p 80 --data $SIZE 192.168.200.60 --rand-source --fast
    done
