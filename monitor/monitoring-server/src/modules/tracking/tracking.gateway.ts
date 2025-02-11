import { MessageBody, SubscribeMessage, WebSocketGateway } from '@nestjs/websockets';
import { TrackingService } from './tracking.service';
import { Server, Socket } from 'socket.io';

@WebSocketGateway({
	cors: {
		origin: 'http://localhost:4200', // Cho phép Angular truy cập
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

    // lắng nghe messge từ client
	@SubscribeMessage('events')
	handleEvent(@MessageBody() data: string) {
		console.log(data);
	}

	// Hàm gửi message từ server đến tất cả client
	sendMessageToClients(message: any) {
		this.server.emit('events', message);
	}
}
