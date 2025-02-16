import { Module } from '@nestjs/common';
import { MongodbService } from './mongodb.service';
import { MongooseModule } from '@nestjs/mongoose';
import { ConfigService } from '@nestjs/config';

@Module({
	imports: [
		MongooseModule.forRootAsync({
			useFactory: (configService: ConfigService) => ({
				uri: configService.get<string>('MONGODB_CONNECTION_STRING'),
			}),
			inject: [ConfigService],
		}),
	],
	providers: [MongodbService],
})
export class MongodbModule {}
