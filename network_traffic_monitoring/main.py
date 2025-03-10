from scapy.sendrecv import AsyncSniffer
from packages.flow_session import generate_session_class
import threading, time
from packages.kafka_service.consumer import KafkaConsumer

def create_sniffer(
    input_interface, NewFlowSession, session_instance, 
):
    def packet_handler(pkt):
        session_instance.on_packet_received(pkt)
    
    return AsyncSniffer(
        iface=input_interface,
        filter="ip and (tcp or udp)",
        prn=packet_handler,
        session=NewFlowSession,
        store=False,
    )

def timelimit(sniffer, session_instance):
    if sniffer.running: 
        x = sniffer.stop()
        session_instance.toPacketList()
    print("\033[31mReached the time limit!\033[0m")

def get_flows():
    input_interface = 'ens33' # network adapter
    output_file = 'data/csv/realtime_flow.csv' # path to save csv file
    # limit = 120 # second
    limit = None # unlimit

    NewFlowSession = generate_session_class(output_file)
    session_instance = NewFlowSession()

    sniffer = create_sniffer(
        input_interface,
        NewFlowSession, 
        session_instance, 
    )

    t = threading.Timer(limit, timelimit, (sniffer, session_instance))

    print('Start get trafic flow')

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
        session_instance.toPacketList()
        while sniffer.results is None:
            time.sleep(1)

    finally:
        sniffer.join()
        if t.is_alive():
            t.cancel()
            t.join()

def predict_and_send_result():
    consumer = KafkaConsumer()
    consumer.consume_messages()

def main():

    get_flows_thread = threading.Thread(target=get_flows, daemon=True) 
    predict_thread = threading.Thread(target=predict_and_send_result, daemon=True)

    get_flows_thread.start()
    predict_thread.start()

    
    get_flows_thread.join()
    predict_thread.join()


if __name__ == "__main__":
    main()
