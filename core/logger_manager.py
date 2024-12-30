import logging
import os
from logging.handlers import RotatingFileHandler
from threading import Lock

import logging
import os
from logging.handlers import RotatingFileHandler
from threading import Lock


class UserContextFilter(logging.Filter):
    """
    A logging filter to add user context (e.g., username) to log messages.
    """
    def __init__(self, username: str):
        super().__init__()
        self.username = username

    def filter(self, record):
        record.username = self.username
        return True


class LoggerManager:
    """
    Manages multiple logger instances in a thread-safe manner.
    Each logger can have different configurations (logfile, levels, etc.).
    """

    _instances = {}
    _lock = Lock()

    @classmethod
    def get_logger(cls,
                   name: str = 'AppLogger',
                   log_file: str = None,
                   log_file_name: str = None,
                   max_file_size: int = 10 * 1024 * 1024,
                   backup_count: int = 3,
                   console_level=logging.WARNING,
                   file_level=logging.DEBUG,
                   username: str = "UnknownUser") -> logging.Logger:
        """
        Retrieve or create a logger instance configured with both console
        and rotating file handlers. Adds a username context to logs.

        :param log_file_name:
        :param name: The name of the logger (default "AppLogger").
        :param log_file: Optional path to the log file. If not provided, uses "core.log".
        :param max_file_size: Max size of the log file in bytes before rotation.
        :param backup_count: Number of backups to keep after rotating.
        :param console_level: Logging level for console output (default WARNING).
        :param file_level: Logging level for file output (default DEBUG).
        :param username: The username to include in log records.
        :return: A configured logger instance.
        """

        # todo: remove log_file
        if log_file is None and log_file_name is None:
            log_file = os.path.join('config', 'logs', 'core.log')

        if log_file_name is not None and log_file is None:
            if log_file_name == 'db':
                log_file = os.path.join('config', 'logs', 'db.log')
            elif log_file_name == 'app':
                log_file = os.path.join('config', 'logs', 'app.log')
            elif log_file_name == 'api':
                log_file = os.path.join('config', 'logs', 'api.log')


        with cls._lock:
            if name in cls._instances:
                # Update username if an instance already exists
                logger = cls._instances[name]
                for handler in logger.handlers:
                    for _filter in handler.filters:
                        if isinstance(_filter, UserContextFilter):
                            _filter.username = username
                return logger

            # Create a new logger
            logger = logging.getLogger(name)
            logger.setLevel(logging.DEBUG)  # Master level

            # Only add handlers if they don't exist
            if not logger.hasHandlers():
                # Console handler
                console_handler = logging.StreamHandler()
                console_handler.setLevel(console_level)

                # Rotating file handler
                file_handler = RotatingFileHandler(
                    filename=log_file,
                    maxBytes=max_file_size,
                    backupCount=backup_count
                )
                file_handler.setLevel(file_level)

                # Common formatter
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s '
                    '- [%(filename)s:%(lineno)d] - %(message)s - User: %(username)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )

                console_handler.setFormatter(formatter)
                file_handler.setFormatter(formatter)

                # Attach handlers
                logger.addHandler(console_handler)
                logger.addHandler(file_handler)

            # Add user context filter
            _filter = UserContextFilter(username)
            logger.addFilter(_filter)

            # Cache the logger
            cls._instances[name] = logger

            return logger
