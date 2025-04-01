import { Component } from '@angular/core';
import { flows } from './data/flow';
import type { EChartsCoreOption } from 'echarts/core';
import { NgxEchartsModule } from 'ngx-echarts';
import { TrackingService } from './tracking.service';
import {
	TitleComponent,
	TooltipComponent,
	LegendComponent,
	GridComponent,
	VisualMapComponent,
} from 'echarts/components';
import * as echarts from 'echarts/core';
import { PieChart, LineChart } from 'echarts/charts';
import { CanvasRenderer } from 'echarts/renderers';
import { UniversalTransition } from 'echarts/features';

// Đăng ký các component cần thiết
echarts.use([
	TitleComponent,
	TooltipComponent,
	LegendComponent,
	PieChart,
	GridComponent,
	VisualMapComponent,
	LineChart,
	CanvasRenderer,
	UniversalTransition,
]);

@Component({
	selector: 'app-dashboard',
	imports: [NgxEchartsModule],
	templateUrl: './dashboard.component.html',
	styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
	flows = flows;

	// traffic pie chart

	trafficPieChartoptions!: EChartsCoreOption;
	updateTrafficPieChartOptions!: EChartsCoreOption;

	// traffic line chart
	trafficLineChartoptions!: EChartsCoreOption;
	updateTrafficLineChartOptions!: EChartsCoreOption;
	trafficLineChartData: any = [];
	
	// ==============
	flowTemps: any = [];

	constructor(private trackingService: TrackingService) {}

	ngOnInit(): void {
        this.initReceiveTrafficPieChart();
		this.initReceiveTrafficLineChart();

		this.onReceiveFlowTable();
		this.onReceiveTrafficTable();
		// this.flowTemps = flows;
	}

	private initReceiveTrafficPieChart() {
		// initialize chart options:
		this.trafficPieChartoptions = {
			title: {
				text: 'Biểu đồ lưu lượng trong 1 giây',
				left: 'center',
			},
			tooltip: {
				trigger: 'item',
				formatter: '{b}: {d}%',
			},
			legend: {
				orient: 'horizontal', // Hiển thị theo hàng ngang
				bottom: '0', // Đặt ở dưới cùng
				left: 'center', // Căn giữa
			},
			label: {
				show: true,
				formatter: '{b}: {d}%', // Hiển thị tên và phần trăm ngay trên biểu đồ
			},
			series: [
				{
					name: 'Tỷ lệ',
					type: 'pie',
					radius: '50%',
					data: [
						{ value: 40, name: 'TCP' },
						{ value: 60, name: 'UDP' },
					],
					emphasis: {
						itemStyle: {
							shadowBlur: 10,
							shadowOffsetX: 0,
							shadowColor: 'rgba(0, 0, 0, 0.5)',
						},
					},
				},
			],
		};
	}

	private initReceiveTrafficLineChart() {
		this.trafficLineChartoptions = {
			title: {
				text: 'Lưu lượng mạng theo thời gian thực',
				left: 'center',
			},
			tooltip: {
				trigger: 'axis',
				formatter: function (params: any) {
					params = params[0];
					var date = new Date(params.name);
					return (
						date.getDate() +
						'/' +
						(date.getMonth() + 1) +
						'/' +
						date.getFullYear() +
						' : ' +
						params.value[1]
					);
				},
				axisPointer: {
					animation: true,
				},
			},
			xAxis: {
				type: 'time',
				splitLine: {
					show: false,
				},
			},
			yAxis: {
				type: 'value',
				boundaryGap: [0, '20%'],
				splitLine: {
					show: true,
				},
			},
			series: [
				{
					// name: 'Fake Data',
					type: 'line',
					showSymbol: false,
					data: this.trafficLineChartData,
				},
			],
		};
	}

    private onReceiveFlowTable() {
		// Lắng nghe sự kiện 'events' từ server
		this.trackingService.listen('flow-tracking').subscribe((data: any) => {
			// console.log('Received message:', data);

			const d = {
				// src_ip: data.data['Source IP'],
				dst_ip: data.data['Dest Post'],
				src_port: data.data['Protocol'],
				dst_port: data.data['Timestamp'],

				protocol: data.data['Flow Duration'],
				timestamp: data.data['Flow Bytes/s'],
				// prediction: data.data.prediction,
				prediction: data.data['Predict'],
			};

			if (this.flowTemps.length >= 10) {
				this.flowTemps.pop();
			}

			this.flowTemps.unshift(d);
		});
	}

	private onReceiveTrafficTable() {
		// Lắng nghe sự kiện 'events' từ server
		this.trackingService.listen('traffic-tracking').subscribe((data: any) => {
			// update series data:
			this.updateTrafficPieChartOptions = {
				series: [
					{
						data: data.trafficPieChart,
					},
				],
			};
            
			this.trafficLineChartData.push(data.trafficLineChart);
			if (this.trafficLineChartData.length > 100) {
				this.trafficLineChartData.shift();
			}

			// update series data:
			this.updateTrafficLineChartOptions = {
				series: [
					{
						data: this.trafficLineChartData,
					},
				],
			};
		});
	}

	ngOnDestroy() {
		this.trackingService.disconnect();
	}
}
