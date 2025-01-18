import logging
import logging.handlers
import os
import tarfile
import zipfile
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from app.config import LoggingConfig

logger = logging.getLogger(__name__)


class ArchiveRotatingFileHandler(TimedRotatingFileHandler):
    """
    Custom handler that archives the log file during each rotation.
    """

    def __init__(
        self,
        filename,
        when="h",
        interval=1,
        backupCount=0,
        encoding=None,
        delay=False,
        utc=False,
        atTime=None,
        errors=None,
        archive_format="zip",
    ):
        """
        Initializes the handler with options for the archive format.

        Arguments:
            filename (str): The name of the log file to rotate.
            when (str): The frequency of rotation (e.g., 'h' for hours, 'd' for days).
            interval (int): The interval of rotation.
            backupCount (int): The number of backup log files to keep.
            encoding (str): The encoding of the log file.
            delay (bool): Whether to delay file opening until the first log entry.
            utc (bool): Whether to use UTC time.
            atTime (datetime): The exact time to perform the rollover (if any).
            errors (str): The error handling strategy for file open errors.
            archive_format (str): The format of the archive file ('zip' or 'gz').

        Raises:
            ValueError: If archive_format is not 'zip' or 'gz'.
        """
        super().__init__(
            filename,
            when,
            interval,
            backupCount,
            encoding,
            delay,
            utc,
            atTime,
            errors,
        )
        if archive_format not in {"zip", "gz"}:
            raise ValueError("archive_format must be either 'zip' or 'gz'")

        self.archive_format = archive_format
        logger.debug(f"Initialized ArchiveRotatingFileHandler with format: {self.archive_format}")

    def doRollover(self):
        """
        Perform log rotation, archive the current log file, and remove old logs.
        Supports both ZIP and GZ formats for archiving.
        """
        super().doRollover()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dir_name = os.path.dirname(self.baseFilename)
        archive_name = os.path.join(dir_name, f"{timestamp}.{self.archive_format}")

        self._archive_log_file(archive_name)  # TODO: send archive to developer
        self._remove_old_logs()

    def _archive_log_file(self, archive_name: str) -> None:
        """
        Archive the current log file to the specified archive name.

        Arguments:
            archive_name (str): The name of the archive file.
        """
        logger.info(f"Archiving {self.baseFilename} to {archive_name}")
        if os.path.exists(self.baseFilename):
            if self.archive_format == "zip":
                self._archive_to_zip(archive_name)
            elif self.archive_format == "gz":
                self._archive_to_gz(archive_name)
        else:
            logger.warning(f"Log file {self.baseFilename} does not exist, skipping archive.")

    def _archive_to_zip(self, archive_name: str) -> None:
        """
        Archive the log file to a ZIP format.

        Arguments:
            archive_name (str): The name of the archive file.
        """
        log = self.getFilesToDelete()[0]
        new_log_name = self._get_log_filename(archive_name)
        with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(log, new_log_name)

    def _archive_to_gz(self, archive_name: str) -> None:
        """
        Archive the log file to a GZ format.

        Arguments:
            archive_name (str): The name of the archive file.
        """
        log = self.getFilesToDelete()[0]
        new_log_name = self._get_log_filename(archive_name)
        with tarfile.open(archive_name, "w:gz") as archive:
            archive.add(log, new_log_name)

    def _get_log_filename(self, archive_name: str) -> str:
        """
        Generate the log file name to be used inside the archive.

        Arguments:
            archive_name (str): The name of the archive file.

        Returns:
            str: The log file name.
        """
        return os.path.splitext(os.path.basename(archive_name))[0] + ".log"

    def _remove_old_logs(self) -> None:
        """
        Remove old log files and any other temporary rotated files.
        """
        files_to_delete = self.getFilesToDelete()
        logger.debug(f"Removing old log files: {files_to_delete}")
        for file in files_to_delete:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    logger.debug(f"Successfully deleted old log file: {file}")
                except Exception as exception:
                    logger.error(f"Error deleting {file}: {exception}")


def setup_logging(config: LoggingConfig) -> None:
    """
    Configure the logging system for the application.

    Sets up logging with a file handler for rotating logs and compressing them into
    the specified archive format. Also configures a stream handler for console output.

    Arguments:
        config (LoggingConfig): Configuration object with logging parameters.
    """
    log_dir = config.DIR
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"app.log")
    logging.basicConfig(
        level=getattr(logging, config.LEVEL.upper(), logging.INFO),
        format=config.FORMAT,
        handlers=[
            ArchiveRotatingFileHandler(
                log_file,
                when="midnight",
                interval=1,
                encoding="utf-8",
                archive_format=config.ARCHIVE_FORMAT,
            ),
            logging.StreamHandler(),
        ],
    )

    # Suppress logs to avoid unnecessary output
    aiogram_logger = logging.getLogger("aiogram.event")
    aiogram_logger.setLevel(logging.CRITICAL)

    # aiosqlite_logger = logging.getLogger("aiosqlite")
    # aiosqlite_logger.setLevel(logging.INFO)

    # httpcore_logger = logging.getLogger("httpcore")
    # httpcore_logger.setLevel(logging.INFO)

    aiohttp_logger = logging.getLogger("aiohttp.access")
    aiohttp_logger.setLevel(logging.WARNING)

    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.WARNING)
