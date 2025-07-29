import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from loguru import logger as _logger

_print_level = "INFO"


def find_project_root():
    """
    Finds the root directory of the project by looking for the .git folder.
    Traverses up the directory tree until it finds .git or reaches the system root.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / ".git").exists():
            return parent
    # fallback to fixed path or warn
    print("Warning: .git not found, using fallback path /app")
    return Path("/app")

def define_log_level(print_level="INFO", logfile_level="DEBUG", name: Optional[str] = None):
    """
    Adjust the log level to above level
    """
    global _print_level
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d")
    log_name = f"{name}_{formatted_date}" if name else formatted_date

    project_root = find_project_root()
    logs_dir = os.path.join(project_root, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    print(f"[Logger Init] Writing logs to: {os.path.join(logs_dir, f'{log_name}.txt')}")

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(os.path.join(logs_dir, f"{log_name}.txt"), level=logfile_level)
    return _logger


# logger = define_log_level()
_logger_instance = define_log_level()
logger = _logger_instance


def log_llm_stream(msg):
    _llm_stream_log(msg)


def set_llm_stream_logfunc(func):
    global _llm_stream_log
    _llm_stream_log = func


def _llm_stream_log(msg):
    if _print_level in ["INFO"]:
        print(msg, end="")