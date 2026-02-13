import logging
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime
import uuid

# Logger Configuration
LOG_FILE = "app.log"
MAX_BYTES = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5

class JSONFormatter(logging.Formatter):
    """
    Formatter to output logs in JSON lines format.
    Enforces the schema: event_name, event_data, timestamp, session_id.
    """
    def format(self, record):
        # Base log record
        log_record = {
            "event_name": getattr(record, "event_name", "UNKNOWN"),
            "event_data": getattr(record, "event_data", {}),
            "timestamp": datetime.utcnow().isoformat() + "Z", # UTC ISO 8601
            "session_id": getattr(record, "session_id", "unknown-session"),
            "level": record.levelname
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)

class SynapseLogger:
    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SynapseLogger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance

    def _setup_logger(self):
        self._logger = logging.getLogger("SynapseLogger")
        self._logger.setLevel(logging.INFO)
        
        # Avoid adding multiple handlers if already configured
        if not self._logger.handlers:
            handler = RotatingFileHandler(
                LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
            )
            handler.setFormatter(JSONFormatter())
            self._logger.addHandler(handler)

    def log_event(self, event_name, event_data, session_id, level="INFO"):
        """
        Logs an event with the specific schema.
        
        :param event_name: String name of the event (use constants from events.py)
        :param event_data: Dictionary containing event-specific data
        :param session_id: String session identifier
        :param level: Logging level (INFO, ERROR, etc.)
        """
        extra = {
            "event_name": event_name,
            "event_data": event_data,
            "session_id": session_id
        }
        
        if level.upper() == "ERROR":
            self._logger.error(f"{event_name} occurred", extra=extra)
        else:
            self._logger.info(f"{event_name} occurred", extra=extra)

# Singleton instance for easy import
logger = SynapseLogger()

def get_session_id():
    """Generates a new session ID"""
    return str(uuid.uuid4())
