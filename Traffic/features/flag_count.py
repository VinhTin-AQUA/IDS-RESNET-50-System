from .context.packet_direction import PacketDirection

class FlagCount:
    """This class extracts features related to the Flags Count."""

    def __init__(self, feature):
        self.feature = feature
        self.flags = {
            "F": "FIN",
            "S": "SYN",
            "R": "RST",
            "P": "PSH",
            "A": "ACK",
            "U": "URG",
            "E": "ECE",
            "C": "CWR",
        }

    def has_flag(self, flag, packet_direction=None) -> bool:
        """Count packets by direction.

        Returns:
            packets_count (int):

        """
        packets = (
            (
                packet
                for packet, direction in self.feature.packets
                if direction == packet_direction
            )
            if packet_direction is not None
            else (packet for packet, _ in self.feature.packets)
        )

        for packet in packets:
            if "TCP" in packet:
                protocol = "TCP"
            elif "UDP" in packet:
                protocol = "UDP"

            if protocol == "TCP" and flag[0] in str(packet["TCP"].flags):
                return 1
            elif protocol == "UDP":
                return 0

        return 0

    def flag_counts(self, flag, packet_direction = None) -> int:
        flags_num = {"PSH": 0,
                    "URG": 0,
                    "FIN": 0,
                    "SYN": 0,
                    "RST": 0,
                    "ACK": 0,
                    "CWR": 0,
                    "ECE": 0,
                    }

        packets = (
            (
                packet
                for packet, direction in self.feature.packets
                if direction == packet_direction
            )
            if packet_direction is not None
            else (packet for packet, _ in self.feature.packets)
        )

        for packet in packets:
            if "TCP" in packet:
                protocol = "TCP"
            elif "UDP" in packet:
                protocol = "UDP"

            if protocol == "TCP" and flag[0] in str(packet["TCP"].flags):
                if packet_direction == PacketDirection.FORWARD:
                    match flag[0]:
                        case "P":
                            flags_num["PSH"] += 1
                        
                        case "U":
                            flags_num["URG"] += 1

                        case "F":
                            flags_num["FIN"] += 1

                        case "S":
                            flags_num["SYN"] += 1

                        case "R":
                            flags_num["RST"] += 1

                        case "A":
                            flags_num["ACK"] += 1
                        
                        case "C":
                            flags_num["CWR"] += 1

                        case "E":
                            flags_num["ECE"] += 1

                elif packet_direction == PacketDirection.REVERSE:
                    match flag[0]:
                        case "P":
                            flags_num["PSH"] += 1

                        case "U":
                            flags_num["URG"] += 1

                        case "F":
                            flags_num["FIN"] += 1

                        case "S":
                            flags_num["SYN"] += 1

                        case "R":
                            flags_num["RST"] += 1

                        case "A":
                            flags_num["ACK"] += 1

                        case "C":
                            flags_num["CWR"] += 1

                        case "E":
                            flags_num["ECE"] += 1

                elif packet_direction == None:
                    match flag[0]:
                        case "P":
                            flags_num["PSH"] += 1

                        case "U":
                            flags_num["URG"] += 1

                        case "F":
                            flags_num["FIN"] += 1

                        case "S":
                            flags_num["SYN"] += 1

                        case "R":
                            flags_num["RST"] += 1

                        case "A":
                            flags_num["ACK"] += 1

                        case "C":
                            flags_num["CWR"] += 1

                        case "E":
                            flags_num["ECE"] += 1

            elif protocol == "UDP":
                pass

        match flag[0]:
            case "P":
                return flags_num["PSH"]

            case "U":
                return flags_num["URG"]

            case "F":
                return flags_num["FIN"]

            case "S":
                return flags_num["SYN"]

            case "R":
                return flags_num["RST"]

            case "A":
                return flags_num["ACK"]
            
            case "C":
                return flags_num["CWR"]

            case "E":
                return flags_num["ECE"]

            case _:
                raise Exception("error flag!")
