import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';


@Injectable({
	providedIn: 'root',
})
export class TrackWsService {
	private socket!: Socket;

	constructor() {
		// this.socket = io('http://localhost:3000'); // Kết nối tới server WebSocket NestJS
	}

	// Lắng nghe sự kiện 'message' từ server
	onMessage(): Observable<any> {
		return new Observable(observer => {
			this.socket.on('events', data => {
				observer.next(data);
			});
		});
	}

	// Ngắt kết nối WebSocket khi không cần thiết
	disconnect() {
		if (this.socket) {
			this.socket.disconnect();
		}
	}
}
