from enum import Enum
from typing import Any
from decimal import Decimal

from . import constants
from packages.flow_realtime import packet_flow_key
from packages.flow_realtime.packet_direction import PacketDirection
from packages.flow_realtime.flag_count import FlagCount
from packages.flow_realtime.flow_bytes import FlowBytes
from packages.flow_realtime.packet_count import PacketCount
from packages.flow_realtime.packet_length import PacketLength
from packages.flow_realtime.packet_time import PacketTime
from .utils import get_statistics

class Flow:
    """This class summarizes the values of the features of the network flows"""

    def __init__(self, packet: Any, direction: Enum):
        """This method initializes an object from the Flow class.

        Args:
            packet (Any): A packet from the network.
            direction (Enum): The direction the packet is going ove the wire.
        """

        (
            self.dest_ip,
            self.src_ip,
            self.src_port,
            self.dest_port,
            self.protocol,
        ) = packet_flow_key.get_packet_flow_key(packet, direction)

        self.packets = []
        self.flow_interarrival_time = []
        self.latest_timestamp = 0
        self.start_timestamp = 0
        self.init_window_size = {
            PacketDirection.FORWARD: -1,
            PacketDirection.REVERSE: -1,
        }

        self.start_active = 0
        self.last_active = 0
        self.active = []
        self.idle = []
        self.sbflow_latest_timestamp = 0
        self.sfcount = 0

        self.forward_bulk_last_timestamp = 0
        self.forward_bulk_start_tmp = 0
        self.forward_bulk_count = 0
        self.forward_bulk_count_tmp = 0
        self.forward_bulk_duration = 0
        self.forward_bulk_packet_count = 0
        self.forward_bulk_size = 0
        self.forward_bulk_size_tmp = 0
        self.backward_bulk_last_timestamp = 0
        self.backward_bulk_start_tmp = 0
        self.backward_bulk_count = 0
        self.backward_bulk_count_tmp = 0
        self.backward_bulk_duration = 0
        self.backward_bulk_packet_count = 0
        self.backward_bulk_size = 0
        self.backward_bulk_size_tmp = 0

        self.fwd_fin = 0
        self.bwd_fin = 0
        self.last_active_update_check = False

    def get_data(self) -> dict:
        """This method obtains the values of the features extracted from each flow.

        Note:
            Only some of the network data plays well together in this list.
            Time-to-live values, window values, and flags cause the data to
            separate out too much.

        Returns:
           list: returns a List of values to be outputted into a csv file.

        """

        flow_bytes = FlowBytes(self)
        flag_count = FlagCount(self)
        packet_count = PacketCount(self)
        packet_length = PacketLength(self)
        packet_time = PacketTime(self)
        
        #flow_iat = get_statistics(self.flow_interarrival_time)
        flow_iat = get_statistics(
            packet_time.get_packet_iat()
        )
        forward_iat = get_statistics(
            packet_time.get_packet_iat(PacketDirection.FORWARD)
        )
        backward_iat = get_statistics(
            packet_time.get_packet_iat(PacketDirection.REVERSE)
        )
        active_stat = get_statistics(self.active)
        idle_stat = get_statistics(self.idle)

        data = {
            # Basic IP information
            "Source IP": self.src_ip,
            "Dest IP": self.dest_ip,
            "Source Port": self.src_port,
            "Dest Post": self.dest_port,
            "Protocol": self.protocol,

            # Basic information from packet times
            "Timestamp": packet_time.get_time_stamp(),
            "Flow Duration": 1e6 * packet_time.get_duration(),
            "Flow Bytes/s": flow_bytes.get_rate(),
            "Flow Packets/s": packet_count.get_rate(),
            "Fwd Packets/s": packet_count.get_rate(PacketDirection.FORWARD),
            "Bwd Packets/s": packet_count.get_rate(PacketDirection.REVERSE),

            # Count total packets by direction
            "Total Fwd Packets": packet_count.get_total(PacketDirection.FORWARD),
            "Total Backward Packets": packet_count.get_total(PacketDirection.REVERSE),

            # Statistical info obtained from Packet lengths
            "Fwd Packets Length Total": packet_length.get_total(PacketDirection.FORWARD),
            "Bwd Packets Length Total": packet_length.get_total(PacketDirection.REVERSE),
            "Fwd Packet Length Max": float(packet_length.get_max(PacketDirection.FORWARD)),
            "Fwd Packet Length Min": float(packet_length.get_min(PacketDirection.FORWARD)),
            "Fwd Packet Length Mean": float(packet_length.get_mean(PacketDirection.FORWARD)),
            "Fwd Packet Length Std": float(packet_length.get_std(PacketDirection.FORWARD)),
            "Bwd Packet Length Max": float(packet_length.get_max(PacketDirection.REVERSE)),
            "Bwd Packet Length Min": float(packet_length.get_min(PacketDirection.REVERSE)),
            "Bwd Packet Length Mean": float(packet_length.get_mean(PacketDirection.REVERSE)),
            "Bwd Packet Length Std": float(packet_length.get_std(PacketDirection.REVERSE)),
            "Packet Length Max": packet_length.get_max(),
            "Packet Length Min": packet_length.get_min(),
            "Packet Length Mean": float(packet_length.get_mean()),
            "Packet Length Std": float(packet_length.get_std()),
            "Packet Length Variance": float(packet_length.get_var()),
            "Fwd Header Length": flow_bytes.get_forward_header_bytes(),
            "Bwd Header Length": flow_bytes.get_reverse_header_bytes(),
            "Fwd Seg Size Min": flow_bytes.get_min_forward_header_bytes(),
            "Avg Fwd Segment Size": flow_bytes.get_fwd_seg_avg(),
            "Avg Bwd Segment Size": flow_bytes.get_bwd_seg_avg(),
            "Fwd Act Data Packets": packet_count.has_payload(PacketDirection.FORWARD),

            # Flows Interarrival Time
            "Flow IAT Mean": float(flow_iat["mean"]),
            "Flow IAT Max": float(flow_iat["max"]),
            "Flow IAT Min": float(flow_iat["min"]),
            "Flow IAT Std": float(flow_iat["std"]),
            "Fwd IAT Total": float(forward_iat["total"]),
            "Fwd IAT Max": float(forward_iat["max"]),
            "Fwd IAT Min": float(forward_iat["min"]),
            "Fwd IAT Mean": float(forward_iat["mean"]),
            "Fwd IAT Std": float(forward_iat["std"]),
            "Bwd IAT Total": float(backward_iat["total"]),
            "Bwd IAT Max": float(backward_iat["max"]),
            "Bwd IAT Min": float(backward_iat["min"]),
            "Bwd IAT Mean": float(backward_iat["mean"]),
            "Bwd IAT Std": float(backward_iat["std"]),

            # Flags statistics
            "Fwd PSH Flags": flag_count.flag_counts("PSH", PacketDirection.FORWARD),
            "Bwd PSH Flags": flag_count.flag_counts("PSH", PacketDirection.REVERSE),
            "Fwd URG Flags": flag_count.flag_counts("URG", PacketDirection.FORWARD),
            "Bwd URG Flags": flag_count.flag_counts("URG", PacketDirection.REVERSE),
            "FIN Flag Count": flag_count.flag_counts("FIN"),
            "SYN Flag Count": flag_count.flag_counts("SYN"),
            "RST Flag Count": flag_count.flag_counts("RST"),
            "PSH Flag Count": flag_count.flag_counts("PSH"),
            "ACK Flag Count": flag_count.flag_counts("ACK"),
            "URG Flag Count": flag_count.flag_counts("URG"),
            "CWE Flag Count": flag_count.flag_counts("CWR"),
            "ECE Flag Count": flag_count.flag_counts("ECE"),

            # Response Time
            "Down/Up Ratio": packet_count.get_down_up_ratio(),
            "Avg Packet Size": packet_length.get_avg(),
            "Init Fwd Win Bytes": self.init_window_size[PacketDirection.FORWARD] if self.init_window_size[PacketDirection.FORWARD] != -1 else 0,
            "Init Bwd Win Bytes": self.init_window_size[PacketDirection.REVERSE] if self.init_window_size[PacketDirection.REVERSE] != -1 else 0,
            
            # New features
            "win_byts_tot": flow_bytes.get_win_tot(),
            "fwd_win_tot": flow_bytes.get_win_tot(PacketDirection.FORWARD),
            "bwd_win_tot": flow_bytes.get_win_tot(PacketDirection.REVERSE),
            "win_byts_mean": flow_bytes.get_win_mean(),
            "fwd_win_mean": flow_bytes.get_win_mean(PacketDirection.FORWARD),
            "bwd_win_mean": flow_bytes.get_win_mean(PacketDirection.REVERSE),
            "win_byts_std": flow_bytes.get_win_std(),
            "fwd_win_std": flow_bytes.get_win_std(PacketDirection.FORWARD),
            "bwd_win_std": flow_bytes.get_win_std(PacketDirection.REVERSE),
            "win_byts_max": flow_bytes.get_win_max(),
            "fwd_win_max": flow_bytes.get_win_max(PacketDirection.FORWARD),
            "bwd_win_max": flow_bytes.get_win_max(PacketDirection.REVERSE),
            "win_byts_min": flow_bytes.get_win_min(),
            "fwd_win_min": flow_bytes.get_win_min(PacketDirection.FORWARD),
            "bwd_win_min": flow_bytes.get_win_min(PacketDirection.REVERSE),
            "zero_win_cnt": flow_bytes.get_zerowin_cnt(),

            # New features end
            "Active Max": float(active_stat["max"]),
            "Active Min": float(active_stat["min"]),
            "Active Mean": float(active_stat["mean"]),
            "Active Std": float(active_stat["std"]),
            "Idle Max": float(idle_stat["max"]),
            "Idle Min": float(idle_stat["min"]),
            "Idle Mean": float(idle_stat["mean"]),
            "Idle Std": float(idle_stat["std"]),

            "Subflow Fwd Packets": packet_count.get_total(PacketDirection.FORWARD)/self.sfcount if self.sfcount != 0 else 0,
            "Subflow Bwd Packets": packet_count.get_total(PacketDirection.REVERSE)/self.sfcount if self.sfcount != 0 else 0,
            "Subflow Fwd Bytes": packet_length.get_total(PacketDirection.FORWARD)/self.sfcount if self.sfcount != 0 else 0,
            "Subflow Bwd Bytes": packet_length.get_total(PacketDirection.REVERSE)/self.sfcount if self.sfcount != 0 else 0,
            "Fwd Avg Bytes/Bulk": float(
                flow_bytes.get_bytes_per_bulk(PacketDirection.FORWARD)
            ),
            "Fwd Avg Packets/Bulk": float(
                flow_bytes.get_packets_per_bulk(PacketDirection.FORWARD)
            ),
            "Bwd Avg Bytes/Bulk": float(
                flow_bytes.get_bytes_per_bulk(PacketDirection.REVERSE)
            ),
            "Bwd Avg Packets/Bulk": float(
                flow_bytes.get_packets_per_bulk(PacketDirection.REVERSE)
            ),

            #some issue
            #"fwd_blk_rate_avg": float(
            #    flow_bytes.get_bulk_rate(PacketDirection.FORWARD)
            #),
            #"bwd_blk_rate_avg": float(
            #    flow_bytes.get_bulk_rate(PacketDirection.REVERSE)
            #),
        }
        #print(self.start_timestamp)
        #print(packet_time.get_packet_iat())
        return data

    def add_packet(self, packet: Any, direction: Enum) -> None:
        """Adds a packet to the current list of packets.

        Args:
            packet: Packet to be added to a flow
            direction: The direction the packet is going in that flow

        """
        # First packet of the flow
        if self.start_timestamp == 0:
            self.start_timestamp = packet.time
            self.latest_timestamp = packet.time
            self.start_active = packet.time
            self.last_active = packet.time

        self.packets.append((packet, direction))

        self.update_flow_bulk(packet, direction)
        self.update_subflow(packet)
        self.update_active_idle(packet.time)
        """
        if self.start_timestamp != 0:
            self.flow_interarrival_time.append(
                1e6 * (packet.time - self.latest_timestamp)
            )
        """
        self.latest_timestamp = max([packet.time, self.latest_timestamp])
        
        if "TCP" in packet:
            if (
                direction == PacketDirection.FORWARD
                and self.init_window_size[direction] == -1
            ):
                self.init_window_size[direction] = packet["TCP"].window
            elif direction == PacketDirection.REVERSE and self.init_window_size[direction] == -1:
                self.init_window_size[direction] = packet["TCP"].window

    def update_subflow(self, packet):
        """Update subflow

        Args:
            packet: Packet to be parse as subflow

        """
        last_timestamp = (
            self.sbflow_latest_timestamp if self.sbflow_latest_timestamp != 0 else packet.time
        )

        if (packet.time - last_timestamp) > constants.CLUMP_TIMEOUT:
            self.sfcount += 1
                
            #self.update_active_idle(packet.time)

        self.sbflow_latest_timestamp = packet.time

    def update_active_idle(self, current_time):
        """Adds a packet to the current list of packets.

        Args:
            packet: Packet to be update active time

        """
        is_active = False

        if (current_time - self.last_active) > constants.ACTIVE_TIMEOUT:
            if (self.last_active - self.start_active) > 0:
                self.active.append((1e6) * (self.last_active - self.start_active))
            self.idle.append((1e6) * (current_time - self.last_active))
            self.start_active = current_time
            self.last_active = current_time
        else:
            self.last_active = current_time
            is_active = True

        if self.last_active_update_check == True and is_active == True:
            self.active.append((1e6) * (self.last_active - self.start_active))

    def update_flow_bulk(self, packet, direction):
        """Update bulk flow

        Args:
            packet: Packet to be parse as bulk

        """
        payload_size = len(PacketCount.get_payload(packet))
        if payload_size == 0:
            return
        if direction == PacketDirection.FORWARD:
            if self.backward_bulk_last_timestamp > self.forward_bulk_start_tmp:
                self.forward_bulk_start_tmp = 0
            if self.forward_bulk_start_tmp == 0:
                self.forward_bulk_start_tmp = packet.time
                self.forward_bulk_last_timestamp = packet.time
                self.forward_bulk_count_tmp = 1
                self.forward_bulk_size_tmp = payload_size
            else:
                if (
                    packet.time - self.forward_bulk_last_timestamp
                ) > constants.CLUMP_TIMEOUT:
                    self.forward_bulk_start_tmp = packet.time
                    self.forward_bulk_last_timestamp = packet.time
                    self.forward_bulk_count_tmp = 1
                    self.forward_bulk_size_tmp = payload_size
                else:  # Add to bulk
                    self.forward_bulk_count_tmp += 1
                    self.forward_bulk_size_tmp += payload_size
                    if self.forward_bulk_count_tmp == constants.BULK_BOUND:
                        self.forward_bulk_count += 1
                        self.forward_bulk_packet_count += self.forward_bulk_count_tmp
                        self.forward_bulk_size += self.forward_bulk_size_tmp
                        self.forward_bulk_duration += (
                            packet.time - self.forward_bulk_start_tmp
                        )
                    elif self.forward_bulk_count_tmp > constants.BULK_BOUND:
                        self.forward_bulk_packet_count += 1
                        self.forward_bulk_size += payload_size
                        self.forward_bulk_duration += (
                            packet.time - self.forward_bulk_last_timestamp
                        )
                    self.forward_bulk_last_timestamp = packet.time
        else:
            if self.forward_bulk_last_timestamp > self.backward_bulk_start_tmp:
                self.backward_bulk_start_tmp = 0
            if self.backward_bulk_start_tmp == 0:
                self.backward_bulk_start_tmp = packet.time
                self.backward_bulk_last_timestamp = packet.time
                self.backward_bulk_count_tmp = 1
                self.backward_bulk_size_tmp = payload_size
            else:
                if (
                    packet.time - self.backward_bulk_last_timestamp
                ) > constants.CLUMP_TIMEOUT:
                    self.backward_bulk_start_tmp = packet.time
                    self.backward_bulk_last_timestamp = packet.time
                    self.backward_bulk_count_tmp = 1
                    self.backward_bulk_size_tmp = payload_size
                else:  # Add to bulk
                    self.backward_bulk_count_tmp += 1
                    self.backward_bulk_size_tmp += payload_size
                    if self.backward_bulk_count_tmp == constants.BULK_BOUND:
                        self.backward_bulk_count += 1
                        self.backward_bulk_packet_count += self.backward_bulk_count_tmp
                        self.backward_bulk_size += self.backward_bulk_size_tmp
                        self.backward_bulk_duration += (
                            packet.time - self.backward_bulk_start_tmp
                        )
                    elif self.backward_bulk_count_tmp > constants.BULK_BOUND:
                        self.backward_bulk_packet_count += 1
                        self.backward_bulk_size += payload_size
                        self.backward_bulk_duration += (
                            packet.time - self.backward_bulk_last_timestamp
                        )
                    self.backward_bulk_last_timestamp = packet.time

    @property
    def duration(self):
        return self.latest_timestamp - self.start_timestamp
