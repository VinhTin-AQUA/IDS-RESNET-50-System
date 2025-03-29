import { Module } from '@nestjs/common';
import { TrackingService } from './tracking.service';
import { TrackingGateway } from './tracking.gateway';
import { TrackingController } from './tracking.controller';
import { TrafficModule } from '../traffic/traffic.module';

@Module({
	providers: [TrackingGateway, TrackingService],
	controllers: [TrackingController],
	imports: [TrafficModule],
})
export class TrackingModule {}
