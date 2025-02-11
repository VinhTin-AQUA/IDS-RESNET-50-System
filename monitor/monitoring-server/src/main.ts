import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
	const app = await NestFactory.create(AppModule);
	// Cho phép CORS
	app.enableCors({
		origin: 'http://localhost:4200', // Chỉ định nguồn được phép
		methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
		credentials: true, // Cho phép gửi cookie, authorization headers
	});
	await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
