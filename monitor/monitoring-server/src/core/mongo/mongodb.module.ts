import { Module } from '@nestjs/common';
import { MongodbService } from './mongodb.service';

@Module({
  providers: [MongodbService]
})
export class MongodbModule {}
