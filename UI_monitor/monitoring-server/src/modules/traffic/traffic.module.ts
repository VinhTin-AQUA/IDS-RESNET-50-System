import { Module } from '@nestjs/common';
import { TrafficService } from './traffic.service';
import { MongooseModule } from '@nestjs/mongoose';
import { Traffic, TrafficSchema } from './entities/traffic.entity';

@Module({
	imports: [
		MongooseModule.forFeature([
			{
				name: Traffic.name,
				schema: TrafficSchema,
				collection: 'traffics',
				discriminators: [],
			},
		]),
	],
	providers: [TrafficService],
	exports: [TrafficService],
})
export class TrafficModule {}
