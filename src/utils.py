import logging
import sys
import json
from datetime import datetime

def setup_logger(name: str = "ai-content-processor"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger

logger = setup_logger()

class PerformanceMonitor:
    @staticmethod
    def log_request(task_type: str, duration_ms: float, status: str, error: str = None):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "task_type": task_type,
            "duration_ms": duration_ms,
            "status": status,
            "error": error
        }
        logger.info(json.dumps(log_entry))
