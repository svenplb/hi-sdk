import logging
from typing import List, Optional, Dict, Any
import time


class SDKLogger:
    def __init__(self, name: str = 'hi_sdk'):
        self.logger = logging.getLogger(name)
        self._setup_logger()

    def _setup_logger(self):
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)


class Metrics:
    def __init__(self):
        self.latencies: List[float] = []
        self.token_counts: List[int] = []
        self.start_time: Optional[float] = None

    def start_request(self):
        self.start_time = time.time()

    def end_request(self) -> float:
        if self.start_time is None:
            return 0.0
        latency = time.time() - self.start_time
        self.latencies.append(latency)
        self.start_time = None
        return latency

    def record_tokens(self, count: int):
        self.token_counts.append(count)

    def get_average_latency(self) -> float:
        return sum(self.latencies) / len(self.latencies) if self.latencies else 0.0

    def get_total_tokens(self) -> int:
        return sum(self.token_counts)

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "average_latency": self.get_average_latency(),
            "total_tokens": self.get_total_tokens(),
            "request_count": len(self.latencies),
            "tokens_per_request": self.get_total_tokens() / len(self.token_counts) if self.token_counts else 0
        }

    def reset(self):
        self.latencies = []
        self.token_counts = []
        self.start_time = None
