import logging
import logging.handlers
import os
from datetime import time

# Attempt to import config settings
try:
    from config import LOG_LEVEL
except ImportError:
    # Fallback if config.py is not available or LOG_LEVEL is not set
    # This might happen during initial setup or if config is misconfigured
    print("Warning: Could not import LOG_LEVEL from config. Using default INFO.")
    LOG_LEVEL = "INFO"

# Ensure logs directory exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        print(f"Error creating log directory {LOG_DIR}: {e}")
        # Fallback to current directory if logs directory cannot be created
        LOG_DIR = "."

LOG_FILE_BASENAME = os.path.join(LOG_DIR, "dandys_world_bot.log")

def setup_logging():
    """
    Configures logging for the application.

    - Logs to both console and a daily rotating file.
    - Log file is stored in the 'logs/' directory.
    - Log level is determined by the LOG_LEVEL environment variable.
    """
    numeric_log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_log_level)

    # --- Console Handler ---
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_log_level) # Set level for console output

    # --- File Handler (Rotating) ---
    # Rotate log files daily at midnight
    # Backup 7 old log files before deleting
    file_handler = logging.handlers.TimedRotatingFileHandler(
        LOG_FILE_BASENAME,
        when="midnight",  # Rotate daily at midnight
        interval=1,       # Interval is 1 day
        backupCount=7,    # Keep 7 old log files
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(numeric_log_level) # Set level for file output

    # Add handlers to the root logger
    # Check if handlers are already added to prevent duplication if setup_logging is called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        logger.addHandler(console_handler)
    if not any(isinstance(h, logging.handlers.TimedRotatingFileHandler) and h.baseFilename == LOG_FILE_BASENAME for h in logger.handlers):
        logger.addHandler(file_handler)

    # Set higher log levels for noisy libraries if needed
    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING) # aiohttp can be verbose

    # Initial log message to confirm setup
    # Use a specific logger instance rather than root logger for this message
    # to ensure module name is correctly captured if desired in formatter.
    initial_logger = logging.getLogger(__name__)
    initial_logger.info(f"Logging configured: Level={LOG_LEVEL}, File='{LOG_FILE_BASENAME}'. Console and rotating file handlers active.")

if __name__ == "__main__":
    # This block is for testing the logging setup directly
    setup_logging()
    test_logger = logging.getLogger("utils_test") # Use a named logger for context

    test_logger.debug("This is a debug message.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")
    test_logger.error("This is an error message.")
    test_logger.critical("This is a critical message.")

    print(f"\nCheck the console output and the file '{LOG_FILE_BASENAME}' (and potentially older rotated files in '{LOG_DIR}/') for these messages.")
    print(f"Log level is set to: {LOG_LEVEL}")
    print("If LOG_LEVEL is INFO, you should not see the DEBUG message in console or file.")

    # Example of how other modules would use the logger:
    # import logging
    # from utils import setup_logging # Call this once at app startup
    # logger = logging.getLogger(__name__) # Get a logger for the current module
    # logger.info("This is a message from my_module.")
