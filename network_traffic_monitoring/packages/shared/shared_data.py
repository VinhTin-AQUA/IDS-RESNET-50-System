import threading

class SharedApi:
    _instance = None
    _lock = threading.Lock()  # Đảm bảo thread-safe

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'lock'):  # Đảm bảo init chỉ chạy 1 lần
            self.lock = threading.Lock()
            
            self.api_base = 'http://e0b7-2401-d800-afb-a79c-2466-93c6-b606-8232.ngrok-free.app'

   
