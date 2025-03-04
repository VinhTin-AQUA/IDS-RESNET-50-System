import argparse
from scapy.sendrecv import AsyncSniffer
from packages.flow_realtime.flow_session import generate_session_class
import threading, time
from packages.kafka_service.consumer import KafkaConsumer

def create_sniffer(
    input_file, input_interface, output_mode, output_file
):
    assert (input_file is None) ^ (input_interface is None)
    
    NewFlowSession = generate_session_class(output_mode, output_file)
    
    if input_file is not None:
        return AsyncSniffer(
            offline=input_file,
            filter="ip and udp",
            prn=lambda x: NewFlowSession.on_convert_pcap_to_csv(NewFlowSession,packet=x),
            session=NewFlowSession,
            store=False,
        )
    else:
        return AsyncSniffer(
            iface=input_interface,
            filter="ip and udp",
            prn=lambda x: NewFlowSession.on_packet_received(NewFlowSession,packet=x),
            session=NewFlowSession,
            store=False,
        )

def timelimit(sniffer):
    if sniffer.running: 
        x = sniffer.stop()
    print("\033[31mReached the time limit!\033[0m")
    
def main2():
    parser = argparse.ArgumentParser()
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i",
        "--interface",
        action="store",
        dest="input_interface",
        help="capture online data from INPUT_INTERFACE",
    )

    input_group.add_argument(
        "-f",
        "--file",
        action="store",
        dest="input_file",
        help="capture offline data from INPUT_FILE",
    )
    
    parameter_group = parser.add_mutually_exclusive_group(required=False)
    parameter_group.add_argument(
        "-t",
        "--timelimit",
        action="store",
        dest="limit",
        default=600, # seconds
        type=int, 
        help="the specified capture time (default is 10 mins)",
    )

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "-c",
        "--csv",
        "--flow",
        action="store_const",
        const="flow",
        dest="output_mode",
        help="output flows as csv",
    )
    
    output_group.add_argument(
        "-m",
        "--mod",
        action="store_const",
        const="predict",
        dest="output_mode",
        help="model used to predict the flow is benign or malicious",
    )

    parser.add_argument(
        "output",
        help="output file name (in flow mode) or predict result (in predict mode)",
    )

    args = parser.parse_args()


    sniffer = create_sniffer(
        args.input_file,
        args.input_interface,
        args.output_mode,
        args.output,
    )
    #if args.limit > 600 or args.limit < 1:
    #    raise ValueError("\033[31mthe range of timelimit is (0,600]!\033[0m")

    if args.output_mode == "flow":
        print("\033[32mIn flow mode\033[0m")
        print("Start to generate csv file!")
        print("----------------------------------")
    else:
        print("\033[32mIn predict mode\033[0m")
        print("Detector started!")
        print("----------------------------------")

    if args.input_file is None:
        t = threading.Timer(args.limit, timelimit, (sniffer,))
        t.start()
        sniffer.start()

        try:
            sniffer.join()
            if t.is_alive():
                t.cancel()
                t.join()
    
        except KeyboardInterrupt:
            print("\033[31mInterrupted by user!\033[0m")
            t.cancel()
            t.join()
            x = sniffer.stop()
            while sniffer.results is None:
                time.sleep(1)
    
        finally:
            sniffer.join()
            if t.is_alive():
                t.cancel()
                t.join()

    elif args.input_file is not None:
        sniffer.start()

        try:
            sniffer.join()

        except KeyboardInterrupt:
            print("\033[31mInterrupted by user!\033[0m")
            x = sniffer.stop()
            while sniffer.results is None:
                time.sleep(1)

        finally:
            sniffer.join()

# ============ conver pcap to csv ===============

def convert_pcap_to_csv():
    
    # convert udp flow
    output = 'csv/udp_flows.csv'
    input_file= 'pcaps/udp_flows.pcap'

    # convert tcp flow
    # output = 'csv/tcp_flows.csv'
    # input_file= 'pcaps/tcp_flows.pcap'

    # input_interface = 'Wi-Fi'
    input_interface = None
    output_mode = 'flow'
    limit= 600 # 600 seconds lay packet trong vong 600 giay

    assert (input_file is None) ^ (input_interface is None)

    NewFlowSession = generate_session_class(output_mode, output)
    sniffer = None

    sniffer = AsyncSniffer(
        offline=input_file,
        filter="ip and udp",
        prn=lambda x: NewFlowSession.on_packet_received_custom(NewFlowSession,packet=x),
        session=NewFlowSession,
        store=False,
    )

    print("\033[32mIn flow mode\033[0m")
    print("Start to generate csv file!")
    print("----------------------------------")

    sniffer.start()
    try:
        sniffer.join()

    except KeyboardInterrupt:
        print("\033[31mInterrupted by user!\033[0m")
        x = sniffer.stop()
        while sniffer.results is None:
            time.sleep(1)

    finally:
        sniffer.join()
        
# ============ get packets realtime ===============

def get_packet_realtime():
    # convert udp flow
    output = 'csv/real_time_flows.csv'
    input_file = None
    input_interface = 'ens33'  # Tên interface của mạng
    output_mode = 'detection'

    assert (input_file is None) ^ (input_interface is None)

    NewFlowSession = generate_session_class(output_mode, output)

    sniffer = AsyncSniffer(
        iface=input_interface,
        filter=f"ip and (udp or tcp)",
    
        prn=lambda x: NewFlowSession.on_packet_received_custom(NewFlowSession, packet=x),
        session=NewFlowSession,
        store=False,
    )

    print("\033[32mIn predict mode\033[0m")
    print("----------------------------------")

    sniffer.start()

    try:
        while True:  # Chạy vô hạn, không giới hạn thời gian
            time.sleep(1)  # Tránh tiêu tốn CPU quá mức
    except KeyboardInterrupt:
        print("\033[31mInterrupted by user!\033[0m")
        sniffer.stop()
    finally:
        sniffer.join()

def handle_packet_in_kafka():
    consumer = KafkaConsumer()
    consumer.consume_messages()  # Vòng lặp này chạy liên tục để nhận dữ liệu Kafka

if __name__ == "__main__":
    # convert_pcap_to_csv()

    consumer_thread = threading.Thread(target=handle_packet_in_kafka, daemon=True) # chay trong luong rieng biet
    consumer_thread.start()
    
    realtime_thread = threading.Thread(target=get_packet_realtime, daemon=True)
    realtime_thread.start()

    while True:
        pass
    

    


