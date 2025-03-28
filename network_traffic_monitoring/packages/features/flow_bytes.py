from scapy.layers.inet import IP, TCP

from .context.packet_direction import PacketDirection
from .packet_time import PacketTime
import numpy

class FlowBytes:
    """Extracts features from the traffic related to the bytes in a flow"""

    def __init__(self, feature):
        self.feature = feature

    def get_bytes(self) -> int:
        """Calculates the amount bytes being transfered.

        Returns:
            int: The amount of bytes.

        """
        feat = self.feature

        return sum(len(packet) for packet, _ in feat.packets)

    def get_rate(self) -> float:
        """Calculates the rate of the bytes being transfered in the current flow.

        Returns:
            float: The bytes/sec sent.

        """
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = 0
        else:
            rate = self.get_bytes() / duration

        return rate

    def get_bytes_sent(self) -> int:
        """Calculates the amount bytes sent from the machine being used to run DoHlyzer.

        Returns:
            int: The amount of bytes.

        """
        feat = self.feature

        return sum(
            len(packet)
            for packet, direction in feat.packets
            if direction == PacketDirection.FORWARD
        )

    def get_sent_rate(self) -> float:
        """Calculates the rate of the bytes being sent in the current flow.

        Returns:
            float: The bytes/sec sent.

        """
        sent = self.get_bytes_sent()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = 0
        else:
            rate = sent / duration

        return rate

    def get_bytes_received(self) -> int:
        """Calculates the amount bytes received.

        Returns:
            int: The amount of bytes.

        """
        packets = self.feature.packets

        return sum(
            len(packet)
            for packet, direction in packets
            if direction == PacketDirection.REVERSE
        )

    def get_received_rate(self) -> float:
        """Calculates the rate of the bytes being received in the current flow.

        Returns:
            float: The bytes/sec received.

        """
        received = self.get_bytes_received()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = 0
        else:
            rate = received / duration

        return rate

    def get_forward_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the same direction as the flow.

        Returns:
            int: The amount of bytes.

        """

        packets = self.feature.packets

        return sum(
            self._header_size(packet)
            for packet, direction in packets
            if direction == PacketDirection.FORWARD
        )

    def get_forward_rate(self) -> float:
        """Calculates the rate of the bytes being going forward
        in the current flow.

        Returns:
            float: The bytes/sec forward.

        """
        forward = self.get_forward_header_bytes()
        duration = PacketTime(self.feature).get_duration()

        if duration > 0:
            rate = forward / duration
        else:
            rate = 0

        return rate

    def _header_size(self, packet):
        """Calculates the amount of header bytes in the packet, UDP is fixed 8 bytes, TCP is 20 + 4 * (data offset field value)

        """
        return 4 * packet["TCP"].dataofs if TCP in packet else 8

    def get_reverse_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the opposite direction as the flow.

        Returns:
            int: The amount of bytes.

        """

        packets = self.feature.packets

        return sum(
            self._header_size(packet)
            for packet, direction in packets
            if direction == PacketDirection.REVERSE
        )

    def get_reverse_rate(self) -> float:
        """Calculates the rate of the bytes being going reverse
        in the current flow.

        Returns:
            float: The bytes/sec reverse.

        """
        reverse = self.get_reverse_header_bytes()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = 0
        else:
            rate = reverse / duration

        return rate

    def get_min_forward_header_bytes(self) -> int:
        """Calculates the minimum amount of header bytes in the header sent in the forward  direction as the flow.

        Returns:
            int: The amount of bytes.

        """

        packets = self.feature.packets

        try:
            if "TCP" in packets[0][0]:
                return min(
                    len(packet["TCP"])
                    for packet, direction in packets
                    if direction == PacketDirection.FORWARD
                )
            else:
                return min(
                    len(packet["UDP"])
                    for packet, direction in packets
                    if direction == PacketDirection.FORWARD
                )
        except:
            # packets list might be empty
            return 0

    def get_min_reverse_header_bytes(self) -> int:
        """Calculates the minimum amount of header bytes in the header sent in the reverse direction as the flow.

        Returns:
            int: The amount of bytes.

        """

        packets = self.feature.packets
        try:
            if "TCP" in packets[0][0]:
                return min(
                    len(packet["TCP"])
                    for packet, direction in packets
                    if direction == PacketDirection.REVERSE
                )
            else:
                return min(
                    len(packet["UDP"])
                    for packet, direction in packets
                    if direction == PacketDirection.REVERSE
                )

        except:
            return 0

    def get_header_in_out_ratio(self) -> float:
        """Calculates the ratio of foward traffic over reverse traffic.

        Returns:
            float: The ratio over reverse traffic.
            If the reverse header bytes is 0 this returns -1 to avoid
            a possible division by 0.

        """
        reverse_header_bytes = self.get_reverse_header_bytes()
        forward_header_bytes = self.get_forward_header_bytes()

        ratio = 0
        if reverse_header_bytes != 0:
            ratio = forward_header_bytes / reverse_header_bytes

        return ratio

    def get_initial_ttl(self) -> int:
        """Obtains the initial time-to-live value.

        Returns:
            int: The initial ttl value in seconds.

        """
        feat = self.feature
        return [packet["IP"].ttl for packet, _ in feat.packets][0]

    def get_bytes_per_bulk(self, packet_direction):
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_count != 0:
                return self.feature.forward_bulk_size / self.feature.forward_bulk_count
        else:
            if self.feature.backward_bulk_count != 0:
                return (
                    self.feature.backward_bulk_size / self.feature.backward_bulk_count
                )
        return 0

    def get_packets_per_bulk(self, packet_direction):
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_count != 0:
                return (
                    self.feature.forward_bulk_packet_count
                    / self.feature.forward_bulk_count
                )
        else:
            if self.feature.backward_bulk_count != 0:
                return (
                    self.feature.backward_bulk_packet_count
                    / self.feature.backward_bulk_count
                )
        return 0

    def get_bulk_rate(self, packet_direction):
        if packet_direction == PacketDirection.FORWARD:
            if self.feature.forward_bulk_count != 0 and self.feature.forward_bulk_duration > 0:
                return (
                    self.feature.forward_bulk_size / self.feature.forward_bulk_duration
                )
        else:
            if self.feature.backward_bulk_count != 0 and self.feature.backward_bulk_duration > 0:
                return (
                    self.feature.backward_bulk_size
                    / self.feature.backward_bulk_duration
                )
        return 0

    def get_fwd_seg_avg(self):
        cnt = len(
                [
                    packet
                    for packet, direction in self.feature.packets
                    if direction == PacketDirection.FORWARD
                ]
            )
        
        if "TCP" in self.feature.packets[0][0]:
            fwd_byts = sum(
                        [
                            len(packet["TCP"])
                            for packet, direction in self.feature.packets
                            if direction == PacketDirection.FORWARD and "TCP" in packet
                        ]
                    )
        elif "UDP" in self.feature.packets[0][0]:
            fwd_byts = sum(
                        [
                            len(packet["UDP"])
                            for packet, direction in self.feature.packets
                            if direction == PacketDirection.FORWARD and "UDP" in packet
                        ]
                    )

        if cnt == 0:
            return 0
        else:
            return fwd_byts/cnt

    def get_bwd_seg_avg(self):
        cnt = len(
                [
                    packet
                    for packet, direction in self.feature.packets
                    if direction == PacketDirection.REVERSE
                ]
            )

        if "TCP" in self.feature.packets[0][0]:
            bwd_byts = sum(
                        [
                            len(packet["TCP"])
                            for packet, direction in self.feature.packets
                            if direction == PacketDirection.REVERSE and "TCP" in packet
                        ]
                    )
        elif "UDP" in self.feature.packets[0][0]:
            bwd_byts = sum(
                        [
                            len(packet["UDP"])
                            for packet, direction in self.feature.packets
                            if direction == PacketDirection.REVERSE and "UDP" in packet
                        ]
                    )

        if cnt == 0:
            return 0
        else:
            return bwd_byts/cnt

    
    def get_win_tot(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction == PacketDirection.FORWARD:
                cnt = len(
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == PacketDirection.FORWARD
                        ]
                    )

                if cnt != 0:
                    return sum(
                            [ 
                                packet["TCP"].window
                                for packet, di in self.feature.packets
                                if di == PacketDirection.FORWARD
                            ]
                        )
                else:
                    return 0

            elif direction == PacketDirection.REVERSE:
                cnt = len(
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == PacketDirection.REVERSE
                        ]
                    )

                if cnt != 0:
                    return sum(
                            [
                                packet["TCP"].window
                                for packet, di in self.feature.packets
                                if di == PacketDirection.REVERSE
                            ]
                        )
                else:
                    return 0

            else:
                cnt = len(
                        [
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

                if cnt != 0:
                    return sum(
                            [
                                packet["TCP"].window
                                for packet, _ in self.feature.packets
                            ]
                        )
                else:
                    return 0

    def get_win_mean(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction != None:
                pkt_list = (
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == direction
                        ]
                    )
            else:
                pkt_list = (
                        [
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

            if direction == PacketDirection.FORWARD:
                if len(pkt_list) > 0:
                    fwd_pkt_win = (
                            [
                                packet["TCP"].window
                                for packet in pkt_list
                            ]
                        )
                    return numpy.mean(fwd_pkt_win)
                else:
                    return 0
            elif direction == PacketDirection.REVERSE:
                if len(pkt_list) > 0:
                    bwd_pkt_win = (
                            [
                                packet["TCP"].window
                                for packet in pkt_list
                            ]
                        )
                    return numpy.mean(bwd_pkt_win)
                else:
                    return 0
            else:
                if len(pkt_list) > 0:
                    pkt_win = (
                            [
                                packet["TCP"].window
                                for packet in pkt_list
                            ]
                        )
                    return numpy.mean(pkt_win)
                else:
                    return 0
    
    def get_win_std(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction != None:
                pkt_list = ( 
                        [   
                            packet
                            for packet, di in self.feature.packets
                            if di == direction
                        ]
                    )
            else:
                pkt_list = ( 
                        [   
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

        if direction == PacketDirection.FORWARD:
            if len(pkt_list) > 0:
                fwd_pkt_win = ( 
                        [   
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                fwd_win_var = numpy.var(fwd_pkt_win)
                return numpy.sqrt(fwd_win_var)
            else:
                return 0
        elif direction == PacketDirection.REVERSE:
            if len(pkt_list) > 0:
                bwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                bwd_win_var = numpy.var(bwd_pkt_win)
                return numpy.sqrt(bwd_win_var)
            else:
                return 0
        else:
            if len(pkt_list) > 0:
                pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                win_var = numpy.var(pkt_win)
                return numpy.sqrt(win_var)
            else:
                return 0
    
    def get_win_max(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction != None:
                pkt_list = (
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == direction
                        ]
                    )
            else:
                pkt_list = (
                        [
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

        if direction == PacketDirection.FORWARD:
            if len(pkt_list) > 0:
                fwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return max(fwd_pkt_win)
            else:
                return 0
        elif direction == PacketDirection.REVERSE:
            if len(pkt_list) > 0:
                bwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return max(bwd_pkt_win)
            else:
                return 0
        else:
            if len(pkt_list) > 0:
                pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return max(pkt_win)
            else:
                return 0

    def get_win_min(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction != None:
                pkt_list = (
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == direction
                        ]
                    )
            else:
                pkt_list = (
                        [
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

        if direction == PacketDirection.FORWARD:
            if len(pkt_list) > 0:
                fwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return min(fwd_pkt_win)
            else:
                return 0
        elif direction == PacketDirection.REVERSE:
            if len(pkt_list) > 0:
                bwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return min(bwd_pkt_win)
            else:
                return 0
        else:
            if len(pkt_list) > 0:
                pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                return min(pkt_win)
            else:
                return 0
    def get_zerowin_cnt(self, direction = None):
        if "UDP" in self.feature.packets[0][0]:
            return 0
        else:
            if direction != None:
                pkt_list = (
                        [
                            packet
                            for packet, di in self.feature.packets
                            if di == direction
                        ]
                    )
            else:
                pkt_list = (
                        [
                            packet
                            for packet, _ in self.feature.packets
                        ]
                    )

        if direction == PacketDirection.FORWARD:
            if len(pkt_list) > 0:
                count = 0
                fwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                for win in fwd_pkt_win:
                    if win == 0:
                        count += 1

                return count
            else:
                return 0
        elif direction == PacketDirection.REVERSE:
            if len(pkt_list) > 0:
                count = 0
                bwd_pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                for win in bwd_pkt_win:
                    if win == 0:
                        count += 1

                return count
            else:
                return 0
        else:
            if len(pkt_list) > 0:
                count = 0
                pkt_win = (
                        [
                            packet["TCP"].window
                            for packet in pkt_list
                        ]
                    )
                for win in pkt_win:
                    if win == 0:
                        count += 1

                return count
            else:
                return 0
