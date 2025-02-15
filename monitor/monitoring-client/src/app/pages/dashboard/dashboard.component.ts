import { Component } from '@angular/core';
import { flows } from './data/flow';
import type { EChartsCoreOption } from 'echarts/core';
import { NgxEchartsModule } from 'ngx-echarts';
import { TrackingService } from './tracking.service';
import { generateRandomNetworkData, getRandomPrediction } from './util';

type DataT = {
	name: string;
	value: [string, number];
};

@Component({
	selector: 'app-dashboard',
	imports: [NgxEchartsModule],
	templateUrl: './dashboard.component.html',
	styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
	flows = flows;

	options!: EChartsCoreOption;
	updateOptions!: EChartsCoreOption;

	// ==============
	flowTemps: any = [];
	timerTemp: any;

	constructor(private trackingService: TrackingService) {}

	ngOnInit(): void {
		this.onRecieFlow();
	}

	private onRecieFlow() {
		// Lắng nghe sự kiện 'events' từ server
		this.trackingService.listen('events').subscribe((data: any) => {
			// console.log('Received message:', data);

			data.data.src_ip;
			data.data.dst_ip;
			data.data.src_port;
			data.data.dst_port;
			data.data.protocol;
			data.data.timestamp;
			data.data.prediction;

			const d = {
				src_ip: data.data.src_ip,
				dst_ip: data.data.dst_ip,
				src_port: data.data.src_port,
				dst_port: data.data.dst_port,
				protocol: data.data.protocol,
				timestamp: data.data.timestamp,
				// prediction: data.data.prediction,
				prediction: getRandomPrediction(),
			};

			if (this.flowTemps.length >= 10) {
				this.flowTemps.shift();
			}

			this.flowTemps.push(d);
		});
	}

	private realTime() {
		this.timerTemp = setInterval(() => {
			const d = generateRandomNetworkData();
			if (this.flowTemps.length >= 10) {
				this.flowTemps.shift();
			}

			this.flowTemps.push(d);
		}, 1000);
	}

	ngOnDestroy() {
		clearInterval(this.timerTemp);
		this.trackingService.disconnect();
	}
}
