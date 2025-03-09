import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Traffic } from './entities/traffic.entity';
import { Model } from 'mongoose';

@Injectable()
export class TrafficService {
    constructor(@InjectModel(Traffic.name) private trafficModel: Model<Traffic>) {}
}
