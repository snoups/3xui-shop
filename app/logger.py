import gzip
import logging
import os
import shutil
import zipfile
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

from app.config import LoggingConfig


class CompressingFileHandler(TimedRotatingFileHandler):
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
        Advanced TimedRotatingFileHandler with support for archiving logs.

        Args:
            filename (str): The name of the log file.
            when (str): Rotation interval ("S", "M", "H", "D", "midnight").
            interval (int): The frequency of rotation.
            backupCount (int): The number of backups to be saved.
            encoding (str): Encoding.
            delay (pool): Open the file only when writing.
            utc (bool): Use UTC time.
            time (Any | None): The exact time for rotation.
            archive_format (str): The archiving format ("zip" or "gz").
        """
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
        if archive_format not in {"zip", "gz"}:
            raise ValueError("archive_format must be either 'zip' or 'gz'")
        self.archive_format = archive_format

    def doRollover(self) -> None:
        """
        Rotates logs and archives the old file depending on the format.
        """
        super().doRollover()

        # Generating the name of the current log file
        log_file = self.rotation_filename(self.baseFilename)
        zip_file = f"{log_file}.zip"

        logging.info(f"Archiving {log_file} to {zip_file}")

        if self.archive_format == "zip":
            # Archiving in .zip format
            zip_file = f"{log_file}.zip"
            with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as archive:
                archive.write(log_file, os.path.basename(log_file))
        elif self.archive_format == "gz":
            # Archiving in .gz format
            gz_file = f"{log_file}.gz"
            with open(log_file, "rb") as log:
                with gzip.open(gz_file, "wb") as archive:
                    shutil.copyfileobj(log, archive)

        # Deleting the original log file after archiving
        os.remove(log_file)


def setup_logging(config: LoggingConfig) -> None:
    """
    Configure the logging system.

    Args:
        config: Logging configuration from the `LoggingConfig` class.
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

    # Set logging level for aiogram to CRITICAL
    aiogram_logger = logging.getLogger("aiogram.event")
    aiogram_logger.setLevel(logging.CRITICAL)
