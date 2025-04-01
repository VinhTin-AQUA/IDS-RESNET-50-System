type TrafficLineChart = {
	name: string;
	value: any;
};

type TrafficPieChart = {
	value: number;
	name: string;
};

export class TrafficTrackingDto {
	trafficLineChart: TrafficLineChart;
	trafficPieChart: TrafficPieChart[];
}
