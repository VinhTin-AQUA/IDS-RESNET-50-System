import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { modules } from './modules';
import { ConfigModule, } from '@nestjs/config';
import { MongodbModule } from './core/mongo/mongodb.module';

@Module({
	imports: [
		...modules,
        ConfigModule.forRoot({ isGlobal: true }),
        MongodbModule
	],
	controllers: [AppController],
	providers: [AppService],
})
export class AppModule {}
