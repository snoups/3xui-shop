import logging
import os
import shutil
from datetime import datetime, timezone
from logging import Logger as BaseLogger
from logging.handlers import TimedRotatingFileHandler

from utils.config import config

LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class ArchivingTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Custom TimedRotatingFileHandler that archives rotated log files using shutil.make_archive()
    and removes the original rotated files.
    """

    def __init__(
        self,
        archive_dir: str,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 0,
        encoding: str = "utf-8",
        utc: bool = True,
    ) -> None:
        """
        Initializes the handler with the specified archive directory.

        Args:
            archive_dir (str): Path to the directory where archived logs will be stored.
            filename (str): Name of the log file.
            when (str): Specifies the type of interval (e.g., 'midnight').
            interval (int): How often the log file should be rotated.
            backupCount (int): Number of backup files to keep.
            encoding (str): Encoding of the log file.
            utc (bool): Use UTC time for rollover.
        """
        self.archive_dir = archive_dir
        os.makedirs(self.archive_dir, exist_ok=True)
        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount,
            encoding=encoding,
            utc=utc,
        )
        self.suffix = "%Y-%m-%d"

    def doRollover(self) -> None:
        """
        Performs a rollover: rotates the log file, archives the rotated file,
        and removes the original rotated file.
        """
        super().doRollover()

        # Get the time of the rollover
        rollover_time = datetime.fromtimestamp(self.rolloverAt, tz=timezone.utc)
        date_str = rollover_time.strftime(self.suffix)

        # Construct the rotated log file name
        rotated_log = self.rotation_filename(f"{self.baseFilename}.{date_str}")

        # Path for the archived log
        archived_log = os.path.join(self.archive_dir, f"{date_str}.log")

        if os.path.exists(rotated_log):
            try:
                # Rename the rotated log file to the archive directory with the date as its name
                os.rename(rotated_log, archived_log)

                # Create a ZIP archive of the rotated log file
                archive_name = os.path.join(self.archive_dir, date_str)
                shutil.make_archive(
                    base_name=archive_name,
                    format="zip",
                    root_dir=self.archive_dir,
                    base_dir=f"{date_str}.log",
                )

                # Remove the original rotated log file after archiving
                os.remove(archived_log)

                # Log the successful archiving
                logging.getLogger(__name__).info(f"Archived log file: {archive_name}.zip")
            except Exception as e:
                # Log any errors that occur during archiving
                logging.getLogger(__name__).error(f"Failed to archive log file {rotated_log}: {e}")
                self.handleError(None)  # Log the error using the standard mechanism


class Logger:
    """
    Logger class to configure and provide logger instances.
    Ensures that all instances use the same ArchivingTimedRotatingFileHandler and StreamHandler.
    """

    _file_handler: ArchivingTimedRotatingFileHandler
    _stream_handler: logging.StreamHandler

    @classmethod
    def _initialize_handlers(cls) -> None:
        """
        Initializes the file and stream handlers if they haven't been initialized yet.
        """
        if not hasattr(cls, "_file_handler"):
            cls._ensure_log_directories_exist()
            today = datetime.now(timezone.utc).date()
            log_filename = cls._get_log_filename(today)

            # Set up the custom archiving timed rotating file handler
            cls._file_handler = ArchivingTimedRotatingFileHandler(
                archive_dir=config.log.archive_dir,
                filename=log_filename,
                when="midnight",  # Rotate logs at midnight UTC
                interval=1,  # Rotate every 1 day
                backupCount=0,  # No backup files; archiving is handled manually
                encoding="utf-8",
                utc=True,
            )

            # Set the formatter for the file handler
            formatter = logging.Formatter(config.log.format, datefmt=LOG_DATE_FORMAT)
            cls._file_handler.setFormatter(formatter)
            cls._set_handler_level(cls._file_handler)

            # Set up the stream handler for console output
            cls._stream_handler = logging.StreamHandler()
            cls._stream_handler.setFormatter(formatter)
            cls._set_handler_level(cls._stream_handler)

    @classmethod
    def _get_log_filename(cls, today: datetime.date) -> str:
        """
        Generates the log file name based on the current date.

        Args:
            today (datetime.date): The current date.

        Returns:
            str: The full path to the log file.
        """
        return os.path.join(config.log.dir, f"{today}.log")

    @classmethod
    def _set_handler_level(cls, handler: logging.Handler) -> None:
        """
        Sets the logging level for the given handler based on the configuration.

        Args:
            handler (logging.Handler): The handler for which to set the logging level.
        """
        log_level_str = config.log.level.upper()
        if not hasattr(logging, log_level_str):
            raise ValueError(f"Invalid LOG_LEVEL: {log_level_str}")
        log_level = getattr(logging, log_level_str)
        handler.setLevel(log_level)

    @classmethod
    def _ensure_log_directories_exist(cls) -> None:
        """
        Ensures that the directories for logs and archives exist.
        """
        os.makedirs(config.log.dir, exist_ok=True)
        os.makedirs(config.log.archive_dir, exist_ok=True)

    def __init__(self, name: str) -> None:
        """
        Initializes the Logger instance.

        Args:
            name (str): The name of the logger.
        """
        self.logger: BaseLogger = logging.getLogger(name)
        Logger._initialize_handlers()
        Logger._add_handlers_to_logger(self.logger)
        self.logger.setLevel(self._get_logger_level())
        self.logger.propagate = False

    @classmethod
    def _add_handlers_to_logger(cls, logger: BaseLogger) -> None:
        """
        Adds the file and stream handlers to the specified logger if they haven't been added already.

        Args:
            logger (logging.Logger): The logger to which handlers will be added.
        """
        if cls._file_handler not in logger.handlers:
            logger.addHandler(cls._file_handler)
        if cls._stream_handler not in logger.handlers:
            logger.addHandler(cls._stream_handler)

    def _get_logger_level(self) -> int:
        """
        Retrieves the logging level from the configuration.

        Returns:
            int: The logging level.
        """
        log_level_str = config.log.level.upper()
        return getattr(logging, log_level_str, logging.INFO)

    def get_logger(self) -> BaseLogger:
        """
        Retrieves the configured logger instance.

        Returns:
            logging.Logger: The configured logger.
        """
        return self.logger
