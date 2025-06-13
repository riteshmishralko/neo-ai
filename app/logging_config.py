import os
import logging
import json
import uuid
import pytz
from datetime import datetime

# Custom log levels
SUCCESS_LEVEL_NUM = 25
FAILED_LEVEL_NUM = 35
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
logging.addLevelName(FAILED_LEVEL_NUM, "FAILED")

def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)

def failed(self, message, *args, **kwargs):
    if self.isEnabledFor(FAILED_LEVEL_NUM):
        self._log(FAILED_LEVEL_NUM, message, args, **kwargs)

logging.Logger.success = success
logging.Logger.failed = failed

class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Ensure all necessary attributes are present with default values
        for attr in ['subfeature', 'request_id', 'method', 'path', 'request_body', 'response_body', 'status_code', 'response_time']:
            if not hasattr(record, attr):
                default_value = 0 if attr in ['status_code', 'response_time'] else 'None'
                setattr(record, attr, default_value)

        return super().format(record)

class SQSLoggingHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            'event_id': str(uuid.uuid4()),
            'timestamp': datetime.fromtimestamp(record.created, tz=pytz.timezone('Asia/Kolkata')).isoformat(),
            'log_level': record.levelname,
            'message': record.getMessage(),
            'service': 'SENTIBOT',
            'project': getattr(record, 'subfeature', 'None'),
            'user_id': getattr(record, 'user_id', ''),
            'session_id': getattr(record, 'session_id', ''),
            'request_id': getattr(record, 'request_id', ''),
            'host': getattr(record, 'host', ''),
            'path': getattr(record, 'path', ''),
            'method': getattr(record, 'method', ''),
            'status_code': getattr(record, 'status_code', 0),
            'request_body': getattr(record, 'request_body', ''),
            'response_body': getattr(record, 'response_body', ''),
            'response_time': getattr(record, 'response_time', 0.0),
            'error_code': getattr(record, 'error_code', ''),
            'stack_trace': getattr(record, 'stack_trace', ''),
            'additional_info': json.dumps(getattr(record, 'additional_info', {}))
        }

        try:
            from app.common.aws_management import send_message_to_queue
            # send_message_to_queue(
            #     sqs_url=os.getenv('SQS_QUEUE_URL', ''),
            #     attributes={},
            #     delay_seconds=0,
            #     body=json.dumps(log_entry)
            # )
        except ImportError:
            print("Error: app.common.aws_management.send_message_to_queue not found.")
        except Exception as e:
            print(f"Failed to send log entry to SQS: {e}")

def setup_logger():
    logger = logging.getLogger('SENTIBOT')
    logger.setLevel(logging.DEBUG)

    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        formatter = CustomFormatter(
            '%(asctime)s - %(name)s | %(levelname)s | %(subfeature)s | %(request_id)s | %(method)s %(path)s | '
            'Request Body: %(request_body)s | Response Body: %(response_body)s | Status: %(status_code)d | '
            'Time: %(response_time).2f ms'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Uncomment the following lines to add SQS handler in production
        # if os.getenv('ENVIRONMENT') == 'production':
        #     sqs_handler = SQSLoggingHandler()
        #     sqs_handler.setFormatter(formatter)
        #     logger.addHandler(sqs_handler)

    return logger

logger = setup_logger()