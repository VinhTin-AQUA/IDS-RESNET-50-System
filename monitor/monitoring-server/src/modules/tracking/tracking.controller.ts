import { Body, Controller, Get, Post } from '@nestjs/common';
import { TrackingGateway } from './tracking.gateway';
import { FlowDto } from './dto/flow.dto';

@Controller('tracking')
export class TrackingController {
	constructor(private trackingGateway: TrackingGateway) {}

	@Post('send')
	sendMessageToClients(@Body() body: FlowDto) {
		this.trackingGateway.sendMessageToClients(body);
		return { success: true, message: 'Message sent to all clients' };
	}
}
