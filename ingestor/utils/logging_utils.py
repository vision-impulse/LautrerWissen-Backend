# Copyright (c) 2025 Vision Impulse GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Authors: Benjamin Bischke

import logging
import os

from logging.handlers import RotatingFileHandler
from django.conf import settings


LOG_DIR = os.getenv("APP_LOG_DIR", "./logs")


def setup_logging(log_file="data-importer.log", level=logging.INFO):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, log_file)

    root_logger = logging.getLogger()
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


def setup_run_logger(run):
    """
    Create a dedicated rotating log file for a pipeline run.
    Returns a logger instance.
    """
    log_dir = os.path.join(LOG_DIR, "pipeline_logs")
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"{run.id}_{run.pipeline_name}.log")

    # Create or get a unique logger per run
    logger_name = f"pipeline.run.{run.id}"
    logger = logging.getLogger(logger_name)

    # Clear previous handlers to avoid duplicate logs
    if logger.handlers:
        for h in logger.handlers[:]:
            logger.removeHandler(h)

    # Create handler
    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=2)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Save log file path to the database
    rel_path = f"pipeline_logs/{os.path.basename(log_path)}"
    run.log_file.name = rel_path
    run.save(update_fields=["log_file"])

    return logger
