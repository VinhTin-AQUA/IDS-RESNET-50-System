import { Component } from '@angular/core';
import { TrackWsService } from './track-ws.service';

@Component({
	selector: 'app-dashboard',
	standalone: true,
	imports: [],
	templateUrl: './dashboard.component.html',
	styleUrl: './dashboard.component.scss',
})
export class DashboardComponent {
	messages: string[] = [];

	constructor(private trackWsService: TrackWsService) {}

	ngOnInit() {
		// Nhận tin nhắn từ server
		// this.trackWsService.onMessage().subscribe(data => {
        //     console.log(data);
		// });
	}

	ngOnDestroy() {
		this.trackWsService.disconnect(); // Ngắt kết nối WebSocket khi component bị hủy
	}
}
