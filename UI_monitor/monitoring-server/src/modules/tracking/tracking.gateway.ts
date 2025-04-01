import { MessageBody, SubscribeMessage, WebSocketGateway } from '@nestjs/websockets';
import { TrackingService } from './tracking.service';
import { Server, Socket } from 'socket.io';
import { TrafficService } from '../traffic/traffic.service';

@WebSocketGateway({
	cors: {
		origin: '*', // Cho phép Angular truy cập
		methods: ['GET', 'POST'],
		credentials: true,
	},
})
export class TrackingGateway {
	constructor(private readonly trackingService: TrackingService) {}

	private server: Server;

	// Khi server WebSocket được khởi tạo
	afterInit(server: Server) {
		this.server = server;
		console.log('WebSocket server initialized');
	}

	// Khi một client kết nối
	handleConnection(client: Socket) {
		console.log(`Client connected: ${client.id}`);
	}

	// Khi một client ngắt kết nối
	handleDisconnect(client: Socket) {
		console.log(`Client disconnected: ${client.id}`);
	}

	/* flow-tracking */
	// lắng nghe messge từ client
	@SubscribeMessage('flow-tracking')
	handleFlowTrackingMessage(@MessageBody() data: string) {
		console.log(data);
	}

	// Hàm gửi message từ server đến tất cả client
	sendFlowTrackingMessageToClient(body: any) {
		this.server.emit('flow-tracking', body);
	}

	/* traffic tracking */
	// lắng nghe messge từ client
	@SubscribeMessage('traffic-tracking')
	handleTrafficTrackingMessage(@MessageBody() data: string) {
		console.log(data);
	}

	// Hàm gửi message từ server đến tất cả client
	sendTrafficTrackingMessageToClient(body: any) {
		this.server.emit('traffic-tracking', body);
	}
}
