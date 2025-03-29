import { Injectable, InternalServerErrorException, NotFoundException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Traffic } from './entities/traffic.entity';
import { FilterQuery, Model, UpdateQuery } from 'mongoose';
import { AddTrafficDto } from './dto/add-traffic.dto';
import { ApiResponse } from 'src/common/response/api-response';

@Injectable()
export class TrafficService {
	constructor(@InjectModel(Traffic.name) private trafficModel: Model<Traffic>) {}

	async findManyByQuery(
		query: FilterQuery<Traffic>,
		fields: string[] = ['']
	): Promise<Traffic[]> {
		try {
			const r = await this.trafficModel.find(query).select(fields.join(' ')).exec();
			if (!r) {
				return [];
			}
			return r;
		} catch {
			return [];
		}
	}

	async findAndUpdate(
		query: FilterQuery<Traffic>,
		updateQuery: UpdateQuery<Traffic>
	): Promise<Traffic> {
		try {
			const updatedBroker = await this.trafficModel.findOneAndUpdate(
				query,
				{ $set: updateQuery },
				{ new: true, runValidators: true } // Trả về broker mới sau khi cập nhật
			);

			// Nếu không tìm thấy tài liệu
			if (!updatedBroker) {
				throw new NotFoundException('House not found with the given query');
			}

			return updatedBroker;
		} catch (error) {
			// Xử lý các lỗi không mong muốn
			throw new InternalServerErrorException(`Error updating house: ${error.message}`);
		}
	}

	async addTraffic(model: AddTrafficDto): Promise<boolean> {
		const newTraffic = new this.trafficModel({
			...model,
			protocol: model.protocol === 6 ? 'Syn' : model.protocol === 17 ? 'UDP' : 'Unknow',
			predict:
				model.predict === 'Group1'
					? 'LDAP'
					: model.predict === 'Group2'
						? 'UDP'
						: model.predict,
		});

		const r = await newTraffic.save({});
		if (r) {
			return true;
		}
		return false;
	}
}
