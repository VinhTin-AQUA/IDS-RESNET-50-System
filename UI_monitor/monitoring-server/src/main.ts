import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { json, urlencoded } from 'express';
import { ValidationPipe } from '@nestjs/common';
import * as bodyParser from 'body-parser';

async function bootstrap() {
	const app = await NestFactory.create(AppModule);

	// Tăng giới hạn body-parser (ví dụ: 10MB)
	app.use(bodyParser.json({ limit: '10mb' }));
	app.use(bodyParser.urlencoded({ limit: '10mb', extended: true }));

	app.useGlobalPipes(
		new ValidationPipe({
			transform: true, // Đảm bảo việc chuyển đổi kiểu dữ liệu từ string sang Date
		})
	);

	// Cho phép CORS
	app.enableCors({
		origin: '*', // Chỉ định nguồn được phép
		methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
		credentials: true, // Cho phép gửi cookie, authorization headers
	});

	await app.listen(process.env.PORT ?? 3000 , '0.0.0.0');
}
bootstrap();
