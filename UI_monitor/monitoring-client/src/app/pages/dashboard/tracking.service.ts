import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { Observable } from 'rxjs';

@Injectable({
	providedIn: 'root',
})
export class TrackingService {
	private socket: Socket;

	constructor() {
		this.socket = io('http://localhost:3000'); // Thay đổi URL nếu server chạy ở địa chỉ khác
	}

	// Lắng nghe sự kiện từ server
	listen(eventName: string): Observable<any> {
		return new Observable(subscriber => {
			this.socket.on(eventName, data => {
				subscriber.next(data);
			});

			return () => {
				this.socket.off(eventName);
			};
		});
	}

	// Gửi sự kiện đến server
	emit(eventName: string, data: any) {
		this.socket.emit(eventName, data);
	}

	// Đóng kết nối socket khi không dùng nữa
	disconnect() {
		this.socket.disconnect();
	}
}
