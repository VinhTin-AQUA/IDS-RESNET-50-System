import csv
from collections import defaultdict

import requests
from scapy.sessions import DefaultSession

from packages.flow_realtime import constants
from packages.flow_realtime.packet_direction import PacketDirection
from packages.flow_realtime.packet_flow_key import get_packet_flow_key
from packages.flow_realtime.flow import Flow
from pandas.core.frame import DataFrame
import os
import pickle
import sys
import threading
import time
from datetime import datetime
import csv
from packages.kafka_service.producer import KafkaProducer
import json

GARBAGE_COLLECT_PACKETS = 10000


class FlowSession(DefaultSession):
    """Creates a list of network flows."""

    def __init__(self, *args, **kwargs):
        
        self.flows = {}
        self.csv_line = 0
        self.ip_list = {}
        self.curr_timestamp = time.time()

        if self.output_mode == "flow":
            output = open(self.output_file, "w")
            self.csv_writer = csv.writer(output)
        elif self.output_mode == "predict":
            with open(os.path.abspath(self.output_file), "rb") as f:
                self.model = pickle.load(f)
        
        self.packets_count = 0
        self.clumped_flows_per_label = defaultdict(list)
        super(FlowSession, self).__init__(*args, **kwargs)
    
    def toPacketList(self):
        # Sniffer finished all the packets it needed to sniff.
        # It is not a good place for this, we need to somehow define a finish signal for AsyncSniffer
        if self.output_mode == "flow":
            print("----------------------------------")
            print("Write the remaining flows into csv file!")
            self.garbage_collect(None)
            print("\033[31mFinish!\033[0m")
            return super(FlowSession, self).toPacketList()
        elif self.output_mode == "predict":
            print("\033[31mTotal unfinished flows: %d \033[0m" %len(self.flows))
            return super(FlowSession, self).toPacketList()


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
        except Exception as e:
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

        print(packet["TCP"].flags)

        if proto == "TCP" and ("F" in str(packet["TCP"].flags)):
            if direction == PacketDirection.FORWARD:
                flow.fwd_fin += 1
            elif direction == PacketDirection.REVERSE:
                flow.bwd_fin += 1
        
        if (packet.time - flow.start_timestamp) > constants.FLOW_TIMEOUT and len(flow.packets) > 0:
            self.garbage_collect(packet.time, packet_flow_key, packet)
            
        else:
            flow.add_packet(packet, direction)
            if proto == "TCP" and (flow.fwd_fin == 1 and flow.bwd_fin == 1):
                self.garbage_collect(packet.time, packet_flow_key)

            elif proto == "TCP" and ("R" in str(packet["TCP"].flags)):
                self.garbage_collect(packet.time, packet_flow_key)
            
            #elif self.packets_count % GARBAGE_COLLECT_PACKETS == 0:
            #    self.garbage_collect(packet.time)
        
        if self.packets_count % GARBAGE_COLLECT_PACKETS == 0:
            self.garbage_collect(packet.time)
        elif (packet.time - self.curr_timestamp) >= constants.FLOW_TIMEOUT:
            self.garbage_collect(packet.time)
            self.curr_timestamp = packet.time

        del flow
        del packet
        #print(self.packets_count)

    def on_packet_received_custom(self, packet):
        direction = PacketDirection.FORWARD
        flow = Flow(packet, direction)
        flow.add_packet(packet, direction)
        data = flow.get_data()  # Lấy dữ liệu từ flow

        ############# du doan #############
        # data_x = DataFrame([data])
        # data_x = data_x[constants.SELECT_FEATURES]
        # res = self.model.predict(data_x)
        value_json = json.dumps(data).encode('utf-8')

        producer = KafkaProducer()
        producer.send_message('flow', value_json)

        ############# luu file #############

        # Kiểm tra xem file có tồn tại và có dữ liệu hay không
        # file_exists = os.path.exists(self.output_file) and os.stat(self.output_file).st_size > 0

        # # Mở file ở chế độ 'a' để ghi tiếp vào cuối file
        # with open(self.output_file, 'a', newline='') as file:
        #     writer = csv.writer(file)

        #     # Nếu file mới hoặc rỗng, ghi header
        #     if not file_exists:
        #         writer.writerow(data.keys())  

        #     # Ghi dữ liệu mới vào file
        #     writer.writerow(data.values())

    def get_flows(self) -> list:
        return self.flows.values()

    def garbage_collect(self, latest_time, flow_key = None, pkt = None) -> None:
        print(213)
        # TODO: Garbage Collection / Feature Extraction should have a separate thread

        flow = self.flows.get(flow_key)
        if self.output_mode == "flow":
            if pkt != None:
                if ("TCP" in flow.packets[0][0] and "TCP" in pkt):
                    if (latest_time - flow.start_timestamp) > constants.FLOW_TIMEOUT:
                        flow.last_active_update_check = True
                        if len(flow.packets) > 1:
                            if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                flow.update_active_idle(flow.packets[-1][0].time)
                        
                        direction = [ pkt[1] for pkt in flow.packets]
                        if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6): # we don't want the unresponse flow to be considered
                            data = flow.get_data()
                        

                            # gửi api

                            if self.csv_line == 0:
                                self.csv_writer.writerow(data.keys())

                            self.csv_writer.writerow(data.values())
                            self.csv_line += 1

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
                        if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                            data = flow.get_data()

                            if self.csv_line == 0:
                                self.csv_writer.writerow(data.keys())

                            self.csv_writer.writerow(data.values())
                            self.csv_line += 1
                            
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
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                                data = flow.get_data()

                                if self.csv_line == 0:
                                    self.csv_writer.writerow(data.keys())

                                self.csv_writer.writerow(data.values())
                                self.csv_line += 1
                            
                                del data

                            del self.flows[flow_key]

                        elif "R" in str(flow.packets[-1][0]["TCP"].flags):
                            flow.last_active_update_check = True
                            if len(flow.packets) > 1:
                                if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                    flow.update_active_idle(flow.packets[-1][0].time)
                            
                            direction = [ pkt[1] for pkt in flow.packets]
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                                data = flow.get_data()
                
                                if self.csv_line == 0:
                                    self.csv_writer.writerow(data.keys())
        
                                self.csv_writer.writerow(data.values())
                                self.csv_line += 1
                                
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
                            
                            direction = [ pkt[1] for pkt in perflow.packets]
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(perflow.packets) >= 6):
                                data = perflow.get_data()
                            
                                if self.csv_line == 0:
                                    self.csv_writer.writerow(data.keys())
                            
                                self.csv_writer.writerow(data.values())
                                self.csv_line += 1
                            
                                del data

                            del self.flows[k]
                            del perflow
                
                    else:
                        keys = list(self.flows.keys())
                        for k in keys:
                            perflow = self.flows.get(k)
                            if (latest_time - perflow.start_timestamp) > constants.FLOW_TIMEOUT:
                                perflow.last_active_update_check = True
                                if len(perflow.packets) > 1:
                                    if (perflow.packets[-1][0].time - perflow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                        perflow.update_active_idle(perflow.packets[-1][0].time)

                                direction = [ pkt[1] for pkt in perflow.packets]                                    
                                if (direction.count(PacketDirection.REVERSE) != 0) and (len(perflow.packets) >= 6):
                                    data = perflow.get_data()
                            
                                    if self.csv_line == 0:
                                        self.csv_writer.writerow(data.keys())

                                    self.csv_writer.writerow(data.values())
                                    self.csv_line += 1
                                
                                    del data
                                
                                del self.flows[k]
                                del perflow      

        elif self.output_mode == "predict":
            if pkt != None:
                if ("TCP" in flow.packets[0][0] and "TCP" in pkt):
                    if (latest_time - flow.start_timestamp) > constants.FLOW_TIMEOUT:
                        flow.last_active_update_check = True
                        if len(flow.packets) > 1:
                            if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                flow.update_active_idle(flow.packets[-1][0].time)

                        direction = [ pkt[1] for pkt in flow.packets]
                        if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                            data = flow.get_data()
                            
                            flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                            data_x = DataFrame([data])
                            data_x = data_x[constants.SELECT_FEATURES]
                            res = self.model.predict(data_x)
                            res = str(res)[1:-1]
                            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                            print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow' .format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))
                            
                            del data
                            del data_x

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
                        if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                            data = flow.get_data()
                        
                            flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                            data_x = DataFrame([data])
                            data_x = data_x[constants.SELECT_FEATURES]
                            res = self.model.predict(data_x)
                            res = str(res)[1:-1]
                            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                            print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow' .format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))

                            del data
                            del data_x

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
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                                data = flow.get_data()
                                
                                flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                                data_x = DataFrame([data])
                                data_x = data_x[constants.SELECT_FEATURES]
                                res = self.model.predict(data_x)
                                res = str(res)[1:-1]
                                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                                print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow'.format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))

                                del data
                                del data_x

                            del self.flows[flow_key]

                    #elif "TCP" in flow.packets[0][0]:
                        elif "R" in str(flow.packets[-1][0]["TCP"].flags):
                            flow.last_active_update_check = True
                            if len(flow.packets) > 1:
                                if (flow.packets[-1][0].time - flow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                    flow.update_active_idle(flow.packets[-1][0].time)
                            
                            direction = [ pkt[1] for pkt in flow.packets]
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(flow.packets) >= 6):
                                data = flow.get_data()
                                
                                flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                                data_x = DataFrame([data])
                                data_x = data_x[constants.SELECT_FEATURES]
                                res = self.model.predict(data_x)
                                res = str(res)[1:-1]
                                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                                print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow' .format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))

                                del data
                                del data_x

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

                            direction = [ pkt[1] for pkt in perflow.packets]
                            if (direction.count(PacketDirection.REVERSE) != 0) and (len(perflow.packets) >= 6):
                                data = perflow.get_data()
                                
                                flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                                data_x = DataFrame([data])
                                data_x = data_x[constants.SELECT_FEATURES]
                                res = self.model.predict(data_x)
                                res = str(res)[1:-1]
                                print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                                print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow' .format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))

                                del data
                                del data_x

                            del self.flows[k]   
                            del perflow
                
                    else:
                        keys = list(self.flows.keys())
                        for k in keys:
                            perflow = self.flows.get(k)
                            if (latest_time - perflow.start_timestamp) > constants.FLOW_TIMEOUT:
                                perflow.last_active_update_check = True
                                if len(perflow.packets) > 1:
                                    if (perflow.packets[-1][0].time - perflow.packets[-2][0].time) <= constants.ACTIVE_TIMEOUT:
                                        perflow.update_active_idle(perflow.packets[-1][0].time)
                                
                                direction = [ pkt[1] for pkt in perflow.packets]
                                if (direction.count(PacketDirection.REVERSE) != 0) and (len(perflow.packets) >= 6):
                                    data = perflow.get_data()
                                    
                                    flow_id = (data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol'])
                                    data_x = DataFrame([data])
                                    data_x = data_x[constants.SELECT_FEATURES]
                                    res = self.model.predict(data_x)
                                    res = str(res)[1:-1]
                                    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3])
                                    print('\033[32m INFO \033[0m [Slow HTTP Attack Detector]','Detect a {0} flow' .format(res),'(src_ip: {0}, dst_ip: {1}, src_port: {2}, dst_port: {3}, protocol: {4})' .format(data['src_ip'], data['dst_ip'], data['src_port'], data['dst_port'], data['protocol']))

                                    del data
                                    del data_x

                                del self.flows[k]
                                del perflow

    

def generate_session_class(output_mode, output_file):
    return type(
        "NewFlowSession",
        (FlowSession,),
        {
            "output_mode": output_mode,
            "output_file": output_file,
        },
    )
