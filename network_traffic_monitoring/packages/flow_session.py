import csv
from collections import defaultdict
from scapy.sessions import DefaultSession
from . import constants
from .features.context.packet_direction import PacketDirection
from .features.context.packet_flow_key import get_packet_flow_key
from .flow import Flow
import os
import time
from scapy.all import get_if_addr, IP
import json
from datetime import datetime
from .kafka_service.producer import KafkaProducer

GARBAGE_COLLECT_PACKETS = 10000

class FlowSession(DefaultSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        self.flows = {}
    
        self.ip_list = {}
        self.curr_timestamp = time.time()
        self.packets_count = 0
        self.clumped_flows_per_label = defaultdict(list)
        self.producer = KafkaProducer()

        # self.model = Resnet50Prediction()

        super(FlowSession, self).__init__(*args, **kwargs)
    
    def toPacketList(self):
        # Sniffer finished all the packets it needed to sniff.
        # It is not a good place for this, we need to somehow define a finish signal for AsyncSniffer
        print("----------------------------------")
        print("Write the remaining flows into csv file!")

        print(6)
        self.garbage_collect(None)
        print("\033[31mFinish!\033[0m")\

    def on_packet_received(self, packet):
        count = 0
        direction = PacketDirection.FORWARD
        proto = None
        if "TCP" in packet:
            proto = "TCP"
        elif "UDP" in packet:
            proto = "UDP"

        try:
            # Creates a key variable to check
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get(packet_flow_key)
        except Exception:
            return

        self.packets_count += 1
        
        # If there is no forward flow with a count of 0
        if flow is None:
            # There might be one of it in reverse
            direction = PacketDirection.REVERSE
            packet_flow_key = get_packet_flow_key(packet, direction)
            flow = self.flows.get(packet_flow_key)

            if flow is None:
                # If no flow exists create a new flow
                direction = PacketDirection.FORWARD
                flow = Flow(packet, direction)
                packet_flow_key = get_packet_flow_key(packet, direction)
                self.flows[packet_flow_key] = flow
         

        
        if proto == "TCP" and ("F" in str(packet["TCP"].flags)):
            if direction == PacketDirection.FORWARD:
                flow.fwd_fin += 1
            elif direction == PacketDirection.REVERSE:
                flow.bwd_fin += 1
       
        # print("(packet.time - flow.start_timestamp) > constants.FLOW_TIMEOUT and len(flow.packets) > 0:", (packet.time - flow.start_timestamp) > constants.FLOW_TIMEOUT and len(flow.packets) > 0)
        # print("packet.time",packet.time)
        # print("flow.start_timestamp",flow.start_timestamp)
        # print("len(flow.packets)",len(flow.packets))


        # print("proto == \"TCP\" and (flow.fwd_fin == 1 and flow.bwd_fin == 1):",proto == "TCP" and (flow.fwd_fin == 1 and flow.bwd_fin == 1))
        # print("proto == \"TCP\" and (\"R\" in str(packet[\"TCP\"].flags)):", proto == "TCP" and ("R" in str(packet["TCP"].flags)))
        # print("(packet.time - self.curr_timestamp) >= constants.FLOW_TIMEOUT", (packet.time - self.curr_timestamp) >= constants.FLOW_TIMEOUT)

        if (packet.time - flow.start_timestamp) > constants.FLOW_TIMEOUT and len(flow.packets) > 0:
            print(1)
            self.garbage_collect(packet.time, packet_flow_key, packet)
            
        else:
            flow.add_packet(packet, direction)
            if proto == "TCP" and (flow.fwd_fin == 1 and flow.bwd_fin == 1):
                print(2)
                self.garbage_collect(packet.time, packet_flow_key)

            elif proto == "TCP" and ("R" in str(packet["TCP"].flags)):
                print(3)
                self.garbage_collect(packet.time, packet_flow_key)
            
            #elif self.packets_count % GARBAGE_COLLECT_PACKETS == 0:
            #    self.garbage_collect(packet.time)
        
        # if self.packets_count % GARBAGE_COLLECT_PACKETS == 0:
        #     print(4)
        #     self.garbage_collect(packet.time)

        print(f"packet.time - self.curr_timestamp: {packet.time - self.curr_timestamp}")

        if (packet.time - self.curr_timestamp) >= constants.FLOW_TIMEOUT:
            print(5)
            self.garbage_collect(packet.time)
            self.curr_timestamp = packet.time

        del flow
        del packet

    def get_flows(self) -> list:
        return self.flows.values()   

    def garbage_collect(self, latest_time, flow_key = None, pkt = None) -> None:
        # print("vao garbage_collect flow_key", flow_key)

        # TODO: Garbage Collection / Feature Extraction should have a separate thread
        flow = self.flows.get(flow_key)
        

        if pkt != None:
            if ("TCP" in flow.packets[0][0] and "TCP" in pkt):
                if (latest_time - flow.start_timestamp) > constants.FLOW_TIMEOUT:
                    flow.last_active_update_check = True
                    if len(flow.packets) > 1:
                        if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                            flow.update_active_idle(flow.packets[-1][0].time)
                    
                    direction = [ pkt[1] for pkt in flow.packets]

                    # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                    if len(flow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                        data = flow.get_data()
                        self.handle_flow(data)
                        del data

                    del self.flows[flow_key]

                    newflow = Flow(pkt, PacketDirection.FORWARD)
                    new_flow_key = get_packet_flow_key(pkt, PacketDirection.FORWARD)
                    self.flows[new_flow_key] = newflow
                    newflow.add_packet(pkt, PacketDirection.FORWARD)
                
                    del newflow
                    del new_flow_key
                    del pkt

            elif ("UDP" in flow.packets[0][0] and "UDP" in pkt):
                if (latest_time - flow.start_timestamp) > constants.FLOW_TIMEOUT:
                    flow.last_active_update_check = True
                    if len(flow.packets) > 1:
                        if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                            flow.update_active_idle(flow.packets[-1][0].time)
                    
                    direction = [ pkt[1] for pkt in flow.packets]

                    # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                    if len(flow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                        data = flow.get_data()

                        self.handle_flow(data)
                        
                        del data

                    del self.flows[flow_key]

                    newflow = Flow(pkt, PacketDirection.FORWARD)
                    new_flow_key = get_packet_flow_key(pkt, PacketDirection.FORWARD)
                    self.flows[flow_key] = newflow
                    newflow.add_packet(pkt, PacketDirection.FORWARD)
                
                    del newflow
                    del new_flow_key
                    del pkt

        else:
            if flow_key != None:
                if "TCP" in flow.packets[0][0]:
                    if (flow.fwd_fin == 1 and flow.bwd_fin == 1 and ("A" in str(flow.packets[-1][0]["TCP"].flags)) and ("F" not in str(flow.packets[-1][0]["TCP"].flags))):
                        flow.last_active_update_check = True
                        if len(flow.packets) > 1:
                            if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                flow.update_active_idle(flow.packets[-1][0].time)
                        
                        direction = [ pkt[1] for pkt in flow.packets]
                        
                        # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                        if len(flow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                            data = flow.get_data()

                            self.handle_flow(data)
                        
                            del data

                        del self.flows[flow_key]

                    elif "R" in str(flow.packets[-1][0]["TCP"].flags):
                        flow.last_active_update_check = True
                        if len(flow.packets) > 1:
                            if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                flow.update_active_idle(flow.packets[-1][0].time)
                        
                        # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                        direction = [ pkt[1] for pkt in flow.packets]
                        # if len(flow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                        data = flow.get_data()
        
                        self.handle_flow(data)
                        
                        del data

                        del self.flows[flow_key]

            else:
                
                if latest_time == None:
                    keys = list(self.flows.keys())
                    for k in keys:
                        perflow = self.flows.get(k)
                        perflow.last_active_update_check = True
                        if len(perflow.packets) > 1:
                            if (perflow.packets[-1][0].time - perflow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                perflow.update_active_idle(perflow.packets[-1][0].time)
                        
                        # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be consideredz
                        direction = [ pkt[1] for pkt in perflow.packets]
                        if len(perflow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                            data = perflow.get_data()
                        
                            self.handle_flow(data)
                        
                            del data

                        del self.flows[k]
                        del perflow
            
                else:
                    keys = list(self.flows.keys())
                    for k in keys:
                        perflow = self.flows.get(k)
                        print("latest_time - perflow.start_timestamp", latest_time - perflow.start_timestamp)
                        # if (latest_time - perflow.start_timestamp) > constants.FLOW_TIMEOUT:
                            
                        perflow.last_active_update_check = True
                        if len(perflow.packets) > 1:
                            if (perflow.packets[-1][0].time - perflow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                perflow.update_active_idle(perflow.packets[-1][0].time)

                        # if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                        direction = [ pkt[1] for pkt in perflow.packets]   
                        print(f"len(perflow.packets): {len(perflow.packets)} >= constants.MIN_PACKAGE_COUNT_PERFLOW {constants.MIN_PACKAGE_COUNT_PERFLOW}", len(perflow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW)                               
                        if len(perflow.packets) >= constants.MIN_PACKAGE_COUNT_PERFLOW:
                            data = perflow.get_data()
                    
                            self.handle_flow(data)
                        
                            del data
                        
                        del self.flows[k]
                        del perflow      


    def save_csv(self, data):
        file_exists = os.path.exists(self.output_file) and os.stat(self.output_file).st_size > 0

        # Mở file ở chế độ 'a' để ghi tiếp vào cuối file
        with open(self.output_file, 'a', newline='') as file:
            writer = csv.writer(file)

            # Nếu file mới hoặc rỗng, ghi header
            if not file_exists:
                writer.writerow(data.keys())  
                
            # Ghi dữ liệu mới vào file
            writer.writerow(data.values())

    def handle_flow(self, data):
        data['Label'] = 'UDP'
        # data['Predict'] = 'Unknow'
        self.save_csv(data)

        # value_json = json.dumps(data).encode('utf-8')
        # self.producer.send_message('flow', value_json)
        

def generate_session_class(output_file):
    return type(
        "NewFlowSession",
        (FlowSession,),
        {
            "output_file": output_file,
        },
    )

