# data_preprocessing_pipeline/utils.py

import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads a list of dictionaries from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        List[Dict[str, Any]]: Parsed list of user data dictionaries.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                logger.warning("Expected a list of dictionaries, found a different structure.")
                return []
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON file: {file_path}")
        return []


def flatten_metadata(meta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flattens a nested dictionary into a single-level dictionary.

    Args:
        meta (Dict[str, Any]): Nested metadata dictionary.

    Returns:
        Dict[str, Any]: Flattened dictionary.
    """
    flat = {}

    def _recurse(sub_dict: Dict[str, Any], prefix: str = ""):
        for key, value in sub_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                _recurse(value, prefix=full_key)
            else:
                flat[full_key] = value

    _recurse(meta)
    return flat
