export class ApiResponse<T> {
    message: string;
    data?: T;
    statusCode: number;
}