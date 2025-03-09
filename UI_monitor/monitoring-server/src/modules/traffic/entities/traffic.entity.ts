import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Mongoose, SchemaTypes, Types } from 'mongoose';
import { PredictionResult } from '../enum/prediction_result.enum';

@Schema()
export class Traffic {
	@Prop({ type: SchemaTypes.ObjectId, auto: true })
	_id: Types.ObjectId;

	@Prop({ type: Number })
	src_ip: string;

	@Prop({ type: Number })
	dst_ip: string;

	@Prop({ type: Number })
	src_port: number;

	@Prop({ type: Number })
	dst_port: number;

	@Prop({ type: Number })
	protocol: number;

	@Prop({ type: Date })
	timestamp: Date; //'2025-02-11 22:39:32'

	@Prop({ type: Number })
	flow_duration: number;

	@Prop({ type: Number })
	flow_byts_s: number;

	@Prop({ type: Number })
	flow_pkts_s: number;

	@Prop({ type: Number })
	fwd_pkts_s: number;

	@Prop({ type: Number })
	bwd_pkts_s: number;

	@Prop({ type: Number })
	tot_fwd_pkts: number;

	@Prop({ type: Number })
	tot_bwd_pkts: number;

	@Prop({ type: Number })
	totlen_fwd_pkts: number;

	@Prop({ type: Number })
	totlen_bwd_pkts: number;

	@Prop({ type: Number })
	fwd_pkt_len_max: number;

	@Prop({ type: Number })
	fwd_pkt_len_min: number;

	@Prop({ type: Number })
	fwd_pkt_len_mean: number;

	@Prop({ type: Number })
	fwd_pkt_len_std: number;

	@Prop({ type: Number })
	bwd_pkt_len_max: number;

	@Prop({ type: Number })
	bwd_pkt_len_min: number;

	@Prop({ type: Number })
	bwd_pkt_len_mean: number;

	@Prop({ type: Number })
	bwd_pkt_len_std: number;

	@Prop({ type: Number })
	pkt_len_max: number;

	@Prop({ type: Number })
	pkt_len_min: number;

	@Prop({ type: Number })
	pkt_len_mean: number;

	@Prop({ type: Number })
	pkt_len_std: number;

	@Prop({ type: Number })
	pkt_len_var: number;

	@Prop({ type: Number })
	fwd_header_len: number;

	@Prop({ type: Number })
	bwd_header_len: number;

	@Prop({ type: Number })
	fwd_seg_size_min: number;

	@Prop({ type: Number })
	fwd_seg_size_avg: number;

	@Prop({ type: Number })
	bwd_seg_size_avg: number;

	@Prop({ type: Number })
	fwd_act_data_pkts: number;

	@Prop({ type: Number })
	flow_iat_mean: number;

	@Prop({ type: Number })
	flow_iat_max: number;

	@Prop({ type: Number })
	flow_iat_min: number;

	@Prop({ type: Number })
	flow_iat_std: number;

	@Prop({ type: Number })
	fwd_iat_tot: number;

	@Prop({ type: Number })
	fwd_iat_max: number;

	@Prop({ type: Number })
	fwd_iat_min: number;

	@Prop({ type: Number })
	fwd_iat_mean: number;

	@Prop({ type: Number })
	fwd_iat_std: number;

	@Prop({ type: Number })
	bwd_iat_tot: number;

	@Prop({ type: Number })
	bwd_iat_max: number;

	@Prop({ type: Number })
	bwd_iat_min: number;

	@Prop({ type: Number })
	bwd_iat_mean: number;

	@Prop({ type: Number })
	bwd_iat_std: number;

	@Prop({ type: Number })
	fwd_psh_flags: number;

	@Prop({ type: Number })
	bwd_psh_flags: number;

	@Prop({ type: Number })
	fwd_urg_flags: number;

	@Prop({ type: Number })
	bwd_urg_flags: number;

	@Prop({ type: Number })
	fin_flag_cnt: number;

	@Prop({ type: Number })
	syn_flag_cnt: number;

	@Prop({ type: Number })
	rst_flag_cnt: number;

	@Prop({ type: Number })
	psh_flag_cnt: number;

	@Prop({ type: Number })
	ack_flag_cnt: number;

	@Prop({ type: Number })
	urg_flag_cnt: number;

	@Prop({ type: Number })
	cwr_flag_cnt: number;

	@Prop({ type: Number })
	ece_flag_cnt: number;

	@Prop({ type: Number })
	down_up_ratio: number;

	@Prop({ type: Number })
	pkt_size_avg: number;

	@Prop({ type: Number })
	init_fwd_win_byts: number;

	@Prop({ type: Number })
	init_bwd_win_byts: number;

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
	active_max: number;

	@Prop({ type: Number })
	active_min: number;

	@Prop({ type: Number })
	active_mean: number;

	@Prop({ type: Number })
	active_std: number;

	@Prop({ type: Number })
	idle_max: number;

	@Prop({ type: Number })
	idle_min: number;

	@Prop({ type: Number })
	idle_mean: number;

	@Prop({ type: Number })
	idle_std: number;

	@Prop({ type: Number })
	subflow_fwd_pkts: number;

	@Prop({ type: Number })
	subflow_bwd_pkts: number;

	@Prop({ type: Number })
	subflow_fwd_byts: number;

	@Prop({ type: Number })
	subflow_bwd_byts: number;

	@Prop({ type: Number })
	fwd_byts_b_avg: number;

	@Prop({ type: Number })
	fwd_pkts_b_avg: number;

	@Prop({ type: Number })
	bwd_byts_b_avg: number;

	@Prop({ type: Number })
	bwd_pkts_b_avg: number;

	@Prop({ type: String, enum: PredictionResult })
	predictionResult: PredictionResult;
}


export type TrafficDocument = HydratedDocument<Traffic>;
export const TrafficSchema = SchemaFactory.createForClass(Traffic);