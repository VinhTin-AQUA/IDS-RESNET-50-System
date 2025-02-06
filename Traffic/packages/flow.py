from enum import Enum
from typing import Any
from decimal import Decimal

from . import constants
from features.context import packet_flow_key
from features.context.packet_direction import PacketDirection
from features.flag_count import FlagCount
from features.flow_bytes import FlowBytes
from features.packet_count import PacketCount
from features.packet_length import PacketLength
from features.packet_time import PacketTime
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
            "src_ip": self.src_ip,
            "dst_ip": self.dest_ip,
            "src_port": self.src_port,
            "dst_port": self.dest_port,
            "protocol": self.protocol,
            # Basic information from packet times
            "timestamp": packet_time.get_time_stamp(),
            "flow_duration": 1e6 * packet_time.get_duration(),
            "flow_byts_s": flow_bytes.get_rate(),
            "flow_pkts_s": packet_count.get_rate(),
            "fwd_pkts_s": packet_count.get_rate(PacketDirection.FORWARD),
            "bwd_pkts_s": packet_count.get_rate(PacketDirection.REVERSE),
            # Count total packets by direction
            "tot_fwd_pkts": packet_count.get_total(PacketDirection.FORWARD),
            "tot_bwd_pkts": packet_count.get_total(PacketDirection.REVERSE),
            # Statistical info obtained from Packet lengths
            "totlen_fwd_pkts": packet_length.get_total(PacketDirection.FORWARD),
            "totlen_bwd_pkts": packet_length.get_total(PacketDirection.REVERSE),
            "fwd_pkt_len_max": float(packet_length.get_max(PacketDirection.FORWARD)),
            "fwd_pkt_len_min": float(packet_length.get_min(PacketDirection.FORWARD)),
            "fwd_pkt_len_mean": float(packet_length.get_mean(PacketDirection.FORWARD)),
            "fwd_pkt_len_std": float(packet_length.get_std(PacketDirection.FORWARD)),
            "bwd_pkt_len_max": float(packet_length.get_max(PacketDirection.REVERSE)),
            "bwd_pkt_len_min": float(packet_length.get_min(PacketDirection.REVERSE)),
            "bwd_pkt_len_mean": float(packet_length.get_mean(PacketDirection.REVERSE)),
            "bwd_pkt_len_std": float(packet_length.get_std(PacketDirection.REVERSE)),
            "pkt_len_max": packet_length.get_max(),
            "pkt_len_min": packet_length.get_min(),
            "pkt_len_mean": float(packet_length.get_mean()),
            "pkt_len_std": float(packet_length.get_std()),
            "pkt_len_var": float(packet_length.get_var()),
            "fwd_header_len": flow_bytes.get_forward_header_bytes(),
            "bwd_header_len": flow_bytes.get_reverse_header_bytes(),
            "fwd_seg_size_min": flow_bytes.get_min_forward_header_bytes(),
            "fwd_seg_size_avg": flow_bytes.get_fwd_seg_avg(),
            "bwd_seg_size_avg": flow_bytes.get_bwd_seg_avg(),
            "fwd_act_data_pkts": packet_count.has_payload(PacketDirection.FORWARD),
            # Flows Interarrival Time
            "flow_iat_mean": float(flow_iat["mean"]),
            "flow_iat_max": float(flow_iat["max"]),
            "flow_iat_min": float(flow_iat["min"]),
            "flow_iat_std": float(flow_iat["std"]),
            "fwd_iat_tot": float(forward_iat["total"]),
            "fwd_iat_max": float(forward_iat["max"]),
            "fwd_iat_min": float(forward_iat["min"]),
            "fwd_iat_mean": float(forward_iat["mean"]),
            "fwd_iat_std": float(forward_iat["std"]),
            "bwd_iat_tot": float(backward_iat["total"]),
            "bwd_iat_max": float(backward_iat["max"]),
            "bwd_iat_min": float(backward_iat["min"]),
            "bwd_iat_mean": float(backward_iat["mean"]),
            "bwd_iat_std": float(backward_iat["std"]),
            # Flags statistics
            "fwd_psh_flags": flag_count.flag_counts("PSH", PacketDirection.FORWARD),
            "bwd_psh_flags": flag_count.flag_counts("PSH", PacketDirection.REVERSE),
            "fwd_urg_flags": flag_count.flag_counts("URG", PacketDirection.FORWARD),
            "bwd_urg_flags": flag_count.flag_counts("URG", PacketDirection.REVERSE),
            "fin_flag_cnt": flag_count.flag_counts("FIN"),
            "syn_flag_cnt": flag_count.flag_counts("SYN"),
            "rst_flag_cnt": flag_count.flag_counts("RST"),
            "psh_flag_cnt": flag_count.flag_counts("PSH"),
            "ack_flag_cnt": flag_count.flag_counts("ACK"),
            "urg_flag_cnt": flag_count.flag_counts("URG"),
            "cwr_flag_cnt": flag_count.flag_counts("CWR"),
            "ece_flag_cnt": flag_count.flag_counts("ECE"),
            # Response Time
            "down_up_ratio": packet_count.get_down_up_ratio(),
            "pkt_size_avg": packet_length.get_avg(),
            "init_fwd_win_byts": self.init_window_size[PacketDirection.FORWARD] if self.init_window_size[PacketDirection.FORWARD] != -1 else 0,
            "init_bwd_win_byts": self.init_window_size[PacketDirection.REVERSE] if self.init_window_size[PacketDirection.REVERSE] != -1 else 0,
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
            "active_max": float(active_stat["max"]),
            "active_min": float(active_stat["min"]),
            "active_mean": float(active_stat["mean"]),
            "active_std": float(active_stat["std"]),
            "idle_max": float(idle_stat["max"]),
            "idle_min": float(idle_stat["min"]),
            "idle_mean": float(idle_stat["mean"]),
            "idle_std": float(idle_stat["std"]),
            "subflow_fwd_pkts": packet_count.get_total(PacketDirection.FORWARD)/self.sfcount if self.sfcount != 0 else 0,
            "subflow_bwd_pkts": packet_count.get_total(PacketDirection.REVERSE)/self.sfcount if self.sfcount != 0 else 0,
            "subflow_fwd_byts": packet_length.get_total(PacketDirection.FORWARD)/self.sfcount if self.sfcount != 0 else 0,
            "subflow_bwd_byts": packet_length.get_total(PacketDirection.REVERSE)/self.sfcount if self.sfcount != 0 else 0,
            "fwd_byts_b_avg": float(
                flow_bytes.get_bytes_per_bulk(PacketDirection.FORWARD)
            ),
            "fwd_pkts_b_avg": float(
                flow_bytes.get_packets_per_bulk(PacketDirection.FORWARD)
            ),
            "bwd_byts_b_avg": float(
                flow_bytes.get_bytes_per_bulk(PacketDirection.REVERSE)
            ),
            "bwd_pkts_b_avg": float(
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
