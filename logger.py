import logging
import os

# Create a logger
logger = logging.getLogger("NetworkToolkit")
logger.setLevel(logging.DEBUG)

# Create file handler
log_file = "network_toolkit_log.txt"
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add handler to logger
if not logger.handlers:
    logger.addHandler(file_handler)

def log_info(message):
    logger.info(message)

def log_error(message):
    logger.error(message)

def log_warning(message):
    logger.warning(message)
