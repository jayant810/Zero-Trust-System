import logging
import json
from datetime import datetime
import os

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"{LOG_DIR}/security.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("zero_trust_logger")

def log_security_event(user_email: str, ip: str, status: str, event_type: str, detail: str = ""):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_email,
        "ip": ip,
        "status": status,
        "event_type": event_type,
        "detail": detail
    }
    logger.info(json.dumps(log_entry))
