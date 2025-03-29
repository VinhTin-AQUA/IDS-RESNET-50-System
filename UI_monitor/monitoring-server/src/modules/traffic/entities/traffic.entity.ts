import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Mongoose, SchemaTypes, Types } from 'mongoose';
import { PredictionResult } from '../enum/prediction_result.enum';

@Schema()
export class Traffic {
	@Prop({ type: SchemaTypes.ObjectId, auto: true })
	_id: Types.ObjectId;

	@Prop({ type: Number })
	destPost: number;

	@Prop({})
	protocol: string;

	@Prop({ type: Date })
	timestamp: Date;

	@Prop({ type: Number })
	flowDuration: number;

	@Prop({ type: Number })
	flowBytesPerSec: number;

	@Prop({ type: Number })
	flowPacketsPerSec: number;

	@Prop({ type: Number })
	fwdPacketsPerSec: number;

	@Prop({ type: Number })
	bwdPacketsPerSec: number;

	@Prop({ type: Number })
	totalFwdPackets: number;

	@Prop({ type: Number })
	totalBackwardPackets: number;

	@Prop({ type: Number })
	fwdPacketsLengthTotal: number;

	@Prop({ type: Number })
	bwdPacketsLengthTotal: number;

	@Prop({ type: Number })
	fwdPacketLengthMax: number;

	@Prop({ type: Number })
	fwdPacketLengthMin: number;

	@Prop({ type: Number })
	fwdPacketLengthMean: number;

	@Prop({ type: Number })
	fwdPacketLengthStd: number;

	@Prop({ type: Number })
	bwdPacketLengthMax: number;

	@Prop({ type: Number })
	bwdPacketLengthMin: number;

	@Prop({ type: Number })
	bwdPacketLengthMean: number;

	@Prop({ type: Number })
	bwdPacketLengthStd: number;

	@Prop({ type: Number })
	packetLengthMax: number;

	@Prop({ type: Number })
	packetLengthMin: number;

	@Prop({ type: Number })
	packetLengthMean: number;

	@Prop({ type: Number })
	packetLengthStd: number;

	@Prop({ type: Number })
	packetLengthVariance: number;

	@Prop({ type: Number })
	fwdHeaderLength: number;

	@Prop({ type: Number })
	bwdHeaderLength: number;

	@Prop({ type: Number })
	fwdSegSizeMin: number;

	@Prop({ type: Number })
	avgFwdSegmentSize: number;

	@Prop({ type: Number })
	avgBwdSegmentSize: number;

	@Prop({ type: Number })
	fwdActDataPackets: number;

	@Prop({ type: Number })
	flowIatMean: number;

	@Prop({ type: Number })
	flowIatMax: number;

	@Prop({ type: Number })
	flowIatMin: number;

	@Prop({ type: Number })
	flowIatStd: number;

	@Prop({ type: Number })
	fwdIatTotal: number;

	@Prop({ type: Number })
	fwdIatMax: number;

	@Prop({ type: Number })
	fwdIatMin: number;

	@Prop({ type: Number })
	fwdIatMean: number;

	@Prop({ type: Number })
	fwdIatStd: number;

	@Prop({ type: Number })
	bwdIatTotal: number;

	@Prop({ type: Number })
	bwdIatMax: number;

	@Prop({ type: Number })
	bwdIatMin: number;

	@Prop({ type: Number })
	bwdIatMean: number;

	@Prop({ type: Number })
	bwdIatStd: number;

	@Prop({ type: Number })
	fwdPshFlags: number;

	@Prop({ type: Number })
	bwdPshFlags: number;

	@Prop({ type: Number })
	fwdUrgFlags: number;

	@Prop({ type: Number })
	bwdUrgFlags: number;

	@Prop({ type: Number })
	finFlagCount: number;

	@Prop({ type: Number })
	synFlagCount: number;

	@Prop({ type: Number })
	rstFlagCount: number;

	@Prop({ type: Number })
	pshFlagCount: number;

	@Prop({ type: Number })
	ackFlagCount: number;

	@Prop({ type: Number })
	urgFlagCount: number;

	@Prop({ type: Number })
	cweFlagCount: number;

	@Prop({ type: Number })
	eceFlagCount: number;

	@Prop({ type: Number })
	downUpRatio: number;

	@Prop({ type: Number })
	avgPacketSize: number;

	@Prop({ type: Number })
	initFwdWinBytes: number;

	@Prop({ type: Number })
	initBwdWinBytes: number;

	@Prop({ type: Number })
	win_byts_tot: number;

	@Prop({ type: Number })
	fwd_win_tot: number;

	@Prop({ type: Number })
	bwd_win_tot: number;

	@Prop({ type: Number })
	win_byts_mean: number;

	@Prop({ type: Number })
	fwd_win_mean: number;

	@Prop({ type: Number })
	bwd_win_mean: number;

	@Prop({ type: Number })
	win_byts_std: number;

	@Prop({ type: Number })
	fwd_win_std: number;

	@Prop({ type: Number })
	bwd_win_std: number;

	@Prop({ type: Number })
	win_byts_max: number;

	@Prop({ type: Number })
	fwd_win_max: number;

	@Prop({ type: Number })
	bwd_win_max: number;

	@Prop({ type: Number })
	win_byts_min: number;

	@Prop({ type: Number })
	fwd_win_min: number;

	@Prop({ type: Number })
	bwd_win_min: number;

	@Prop({ type: Number })
	zero_win_cnt: number;

	@Prop({ type: Number })
	activeMax: number;

	@Prop({ type: Number })
	activeMin: number;

	@Prop({ type: Number })
	activeMean: number;

	@Prop({ type: Number })
	activeStd: number;

	@Prop({ type: Number })
	idleMax: number;

	@Prop({ type: Number })
	idleMin: number;

	@Prop({ type: Number })
	idleMean: number;

	@Prop({ type: Number })
	idleStd: number;

	@Prop({ type: Number })
	subflowFwdPackets: number;

	@Prop({ type: Number })
	subflowBwdPackets: number;

	@Prop({ type: Number })
	subflowFwdBytes: number;

	@Prop({ type: Number })
	subflowBwdBytes: number;

	@Prop({ type: Number })
	fwdAvgBytesPerBulk: number;

	@Prop({ type: Number })
	fwdAvgPacketsPerBulk: number;

	@Prop({ type: Number })
	bwdAvgBytesPerBulk: number;

	@Prop({ type: Number })
	bwdAvgPacketsPerBulk: number;

	@Prop({ type: Number })
	fwdAvgBulkRate: number;

	@Prop({ type: Number })
	bwdAvgBulkRate: number;

	@Prop({ type: String, enum: PredictionResult })
	predict: PredictionResult;
}

export type TrafficDocument = HydratedDocument<Traffic>;
export const TrafficSchema = SchemaFactory.createForClass(Traffic);
