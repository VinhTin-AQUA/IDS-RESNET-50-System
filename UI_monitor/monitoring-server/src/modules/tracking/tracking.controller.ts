import { Body, Controller, Get, Post } from '@nestjs/common';
import { TrackingGateway } from './tracking.gateway';
import { FlowTrackingDto } from './dto/flow-tracking.dto';
import { TrafficService } from '../traffic/traffic.service';
import { TrafficTrackingDto } from './dto/traffic-tracking.dto';

@Controller('tracking')
export class TrackingController {
	constructor(
		private trackingGateway: TrackingGateway,
		private trafficSevice: TrafficService
	) {}

	@Post('flow-tracking')
	async sendFlowTrackingClients(@Body() body: FlowTrackingDto) {
		this.trackingGateway.sendFlowTrackingMessageToClient(body);

		const traffic = {
			destPost: body.data['Dest Post'],
			protocol: body.data['Protocol'],
			timestamp: body.data['Timestamp'],
			flowDuration: body.data['Flow Duration'],
			flowBytesPerSec: body.data['Flow Bytes/s'],
			flowPacketsPerSec: body.data['Flow Packets/s'],
			fwdPacketsPerSec: body.data['Fwd Packets/s'],
			bwdPacketsPerSec: body.data['Bwd Packets/s'],
			totalFwdPackets: body.data['Total Fwd Packets'],
			totalBackwardPackets: body.data['Total Backward Packets'],
			fwdPacketsLengthTotal: body.data['Fwd Packets Length Total'],
			bwdPacketsLengthTotal: body.data['Bwd Packets Length Total'],
			fwdPacketLengthMax: body.data['Fwd Packet Length Max'],
			fwdPacketLengthMin: body.data['Fwd Packet Length Min'],
			fwdPacketLengthMean: body.data['Fwd Packet Length Mean'],
			fwdPacketLengthStd: body.data['Fwd Packet Length Std'],
			bwdPacketLengthMax: body.data['Bwd Packet Length Max'],
			bwdPacketLengthMin: body.data['Bwd Packet Length Min'],
			bwdPacketLengthMean: body.data['Bwd Packet Length Mean'],
			bwdPacketLengthStd: body.data['Bwd Packet Length Std'],
			packetLengthMax: body.data['Packet Length Max'],
			packetLengthMin: body.data['Packet Length Min'],
			packetLengthMean: body.data['Packet Length Mean'],
			packetLengthStd: body.data['Packet Length Std'],
			packetLengthVariance: body.data['Packet Length Variance'],
			fwdHeaderLength: body.data['Fwd Header Length'],
			bwdHeaderLength: body.data['Bwd Header Length'],
			fwdSegSizeMin: body.data['Fwd Seg Size Min'],
			avgFwdSegmentSize: body.data['Avg Fwd Segment Size'],
			avgBwdSegmentSize: body.data['Avg Bwd Segment Size'],
			fwdActDataPackets: body.data['Fwd Act Data Packets'],
			flowIatMean: body.data['Flow IAT Mean'],
			flowIatMax: body.data['Flow IAT Max'],
			flowIatMin: body.data['Flow IAT Min'],
			flowIatStd: body.data['Flow IAT Std'],
			fwdIatTotal: body.data['Fwd IAT Total'],
			fwdIatMax: body.data['Fwd IAT Max'],
			fwdIatMin: body.data['Fwd IAT Min'],
			fwdIatMean: body.data['Fwd IAT Mean'],
			fwdIatStd: body.data['Fwd IAT Std'],
			bwdIatTotal: body.data['Bwd IAT Total'],
			bwdIatMax: body.data['Bwd IAT Max'],
			bwdIatMin: body.data['Bwd IAT Min'],
			bwdIatMean: body.data['Bwd IAT Mean'],
			bwdIatStd: body.data['Bwd IAT Std'],
			fwdPshFlags: body.data['Fwd PSH Flags'],
			bwdPshFlags: body.data['Bwd PSH Flags'],
			fwdUrgFlags: body.data['Fwd URG Flags'],
			bwdUrgFlags: body.data['Bwd URG Flags'],
			finFlagCount: body.data['FIN Flag Count'],
			synFlagCount: body.data['SYN Flag Count'],
			rstFlagCount: body.data['RST Flag Count'],
			pshFlagCount: body.data['PSH Flag Count'],
			ackFlagCount: body.data['ACK Flag Count'],
			urgFlagCount: body.data['URG Flag Count'],
			cweFlagCount: body.data['CWE Flag Count'],
			eceFlagCount: body.data['ECE Flag Count'],
			downUpRatio: body.data['Down/Up Ratio'],
			avgPacketSize: body.data['Avg Packet Size'],
			initFwdWinBytes: body.data['Init Fwd Win Bytes'],
			initBwdWinBytes: body.data['Init Bwd Win Bytes'],
			win_byts_tot: body.data['win_byts_tot'],
			fwd_win_tot: body.data['fwd_win_tot'],
			bwd_win_tot: body.data['bwd_win_tot'],
			win_byts_mean: body.data['win_byts_mean'],
			fwd_win_mean: body.data['fwd_win_mean'],
			bwd_win_mean: body.data['bwd_win_mean'],
			win_byts_std: body.data['win_byts_std'],
			fwd_win_std: body.data['fwd_win_std'],
			bwd_win_std: body.data['bwd_win_std'],
			win_byts_max: body.data['win_byts_max'],
			fwd_win_max: body.data['fwd_win_max'],
			bwd_win_max: body.data['bwd_win_max'],
			win_byts_min: body.data['win_byts_min'],
			fwd_win_min: body.data['fwd_win_min'],
			bwd_win_min: body.data['bwd_win_min'],
			zero_win_cnt: body.data['zero_win_cnt'],
			activeMax: body.data['Active Max'],
			activeMin: body.data['Active Min'],
			activeMean: body.data['Active Mean'],
			activeStd: body.data['Active Std'],
			idleMax: body.data['Idle Max'],
			idleMin: body.data['Idle Min'],
			idleMean: body.data['Idle Mean'],
			idleStd: body.data['Idle Std'],
			subflowFwdPackets: body.data['Subflow Fwd Packets'],
			subflowBwdPackets: body.data['Subflow Bwd Packets'],
			subflowFwdBytes: body.data['Subflow Fwd Bytes'],
			subflowBwdBytes: body.data['Subflow Bwd Bytes'],
			fwdAvgBytesPerBulk: body.data['Fwd Avg Bytes/Bulk'],
			fwdAvgPacketsPerBulk: body.data['Fwd Avg Packets/Bulk'],
			bwdAvgBytesPerBulk: body.data['Bwd Avg Bytes/Bulk'],
			bwdAvgPacketsPerBulk: body.data['Bwd Avg Packets/Bulk'],
			fwdAvgBulkRate: body.data['Fwd Avg Bulk Rate'],
			bwdAvgBulkRate: body.data['Bwd Avg Bulk Rate'],
			predict: body.data['Predict'],
		};

        await this.trafficSevice.addTraffic(traffic)
		return { success: true, message: 'Message sent to all clients' };
	}

    @Post('traffic-tracking')
    sendTrafficTrackingToClients(@Body() body: TrafficTrackingDto) {
        this.trackingGateway.sendTrafficTrackingMessageToClient(body);
        return body;
    }
}
