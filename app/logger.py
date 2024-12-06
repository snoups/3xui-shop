import gzip
import logging
import os
import shutil
import zipfile
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

from app.config import LoggingConfig


class CompressingFileHandler(TimedRotatingFileHandler):
    """
    Advanced TimedRotatingFileHandler with support for archiving logs.

    Attributes:
        archive_format (str): Format for archiving log files ("zip" or "gz").
    """

    def __init__(
        self,
        filename: str,
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 0,
        encoding: str = None,
        delay: bool = False,
        utc: bool = False,
        atTime=None,
        archive_format: str = "zip",
    ) -> None:
        """
        Initialize the file handler with archiving capabilities.

        Args:
            filename (str): Name of the log file.
            when (str): Rotation interval ("S", "M", "H", "D", "midnight").
            interval (int): Frequency of rotation.
            backupCount (int): Number of backups to keep.
            encoding (str): Encoding of the log file. Defaults to None.
            delay (bool): Whether to delay file creation until writing.
            utc (bool): Use UTC time for log rotation.
            atTime (Optional[datetime.time]): Exact time for rotation.
            archive_format (str): Format for archived logs ("zip" or "gz").

        Raises:
            ValueError: If `archive_format` is not "zip" or "gz".
        """
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        if archive_format not in {"zip", "gz"}:
            raise ValueError("archive_format must be either 'zip' or 'gz'")
        self.archive_format = archive_format

    def doRollover(self) -> None:
        """
        Perform log rotation and archive the old log file.

        Archives the rotated log file in the specified format ("zip" or "gz"),
        then deletes the original log file to save space.
        """
        super().doRollover()

        # Generate the name of the current log file
        log_file = self.rotation_filename(self.baseFilename)

        if self.archive_format == "zip":
            # Archive in .zip format
            zip_file = f"{log_file}.zip"
            logging.info(f"Archiving {log_file} to {zip_file}")
            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.write(log_file, os.path.basename(log_file))
        elif self.archive_format == "gz":
            # Archive in .gz format
            gz_file = f"{log_file}.gz"
            logging.info(f"Archiving {log_file} to {gz_file}")
            with open(log_file, "rb") as log:
                with gzip.open(gz_file, "wb") as archive:
                    shutil.copyfileobj(log, archive)

        # Remove the original log file
        os.remove(log_file)


def setup_logging(config: LoggingConfig) -> None:
    """
    Configure the logging system for the application.

    Sets up a logging system with a file handler for rotating logs and compressing them
    into the specified archive format. Also configures a stream handler for console output.

    Args:
        config (LoggingConfig): Logging configuration object.
    """
    log_dir = config.DIR
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.LEVEL.upper(), logging.INFO),
        format=config.FORMAT,
        handlers=[
            CompressingFileHandler(
                filename=os.path.join(log_dir, f"{datetime.now(timezone.utc).date()}.log"),
                when="midnight",
                interval=1,
                backupCount=7,
                encoding="utf-8",
                archive_format=config.ARCHIVE_FORMAT,
            ),
            logging.StreamHandler(),
        ],
    )

    # Suppress aiogram logs to avoid unnecessary output
    aiogram_logger = logging.getLogger("aiogram.event")
    aiogram_logger.setLevel(logging.CRITICAL)
