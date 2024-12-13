import os
import sys
import logging
from datetime import datetime

def setup_logging(log_dir='logs'):
    """
    Set up logging configuration with a dynamic log file name
    
    Args:
        log_dir (str): Directory to store log files
    
    Returns:
        logging.Logger: Configured logger
    """
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Generate a log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"app_log_{timestamp}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Logging format
    logging_format = "[%(asctime)s: %(levelname)s: %(module)s: %(funcName)s: %(message)s]"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=logging_format,
        handlers=[
            logging.FileHandler(log_filepath),  # Log to file
            logging.StreamHandler(sys.stdout)   # Log to console
        ]
    )
    
    # Create a custom logger
    logger = logging.getLogger("csv_chat_app")
    
    return logger

# Create a global logger
logger = setup_logging()