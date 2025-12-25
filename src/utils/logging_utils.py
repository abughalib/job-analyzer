import logging
import logging.handlers
import sys
from pathlib import Path
from utils.app_config import LoggingConfig, LogLevel


def setup_logging(config: LoggingConfig):
    """
    Sets up the logging configuration for the application to ensuring all logs
    from all modules are captured and formatted correctly.
    """

    # Create logger
    root_logger = logging.getLogger()

    # clear existing handlers
    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(config.level.value)

    # Create formatter
    formatter = logging.Formatter(config.format)

    # Console Handler
    if config.console_logging:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(config.level.value)
        root_logger.addHandler(console_handler)

    # File Handler
    if config.file_logging:
        log_file_path = Path(config.file_path)

        # Ensure directory exists
        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=config.max_size_mb * 1024 * 1024,
                backupCount=config.backup_count,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(config.level.value)
            root_logger.addHandler(file_handler)

        except Exception as e:
            # If we can't file log, print to stderr but don't crash
            print(
                f"Failed to setup file logging at {log_file_path}: {e}", file=sys.stderr
            )

    # Set external libraries to WARNING to reduce noise, unless DEBUG is set
    if config.level != LogLevel.DEBUG:
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        # Add other libraries here if needed

    logging.info(f"Logging initialized. Level: {config.level.value}")
    if config.file_logging:
        logging.info(f"Logging to file: {config.file_path}")
