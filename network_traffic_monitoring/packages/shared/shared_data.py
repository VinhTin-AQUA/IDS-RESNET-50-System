import threading

class SharedState:
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
            self.current_number_of_flow_in_flow_topic = 0
            self.enable_producer = True

    def increase_flow(self):
        with self.lock:
            self.current_number_of_flow_in_flow_topic += 1

    def decrease_flow(self):
        with self.lock:
            self.current_number_of_flow_in_flow_topic -= 1

    def update_producer(self, flag: bool):
        with self.lock:
            self.enable_producer = flag