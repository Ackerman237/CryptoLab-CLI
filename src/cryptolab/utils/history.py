"""Local analysis history logger using JSON Lines."""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

HISTORY_DIR_NAME = ".cryptolab_history"
HISTORY_FILE_NAME = "history.jsonl"

# Sensitive parameter keys that should never be logged
SENSITIVE_PARAM_KEYS = {
    "key", "iv", "password", "secret", "salt", "private_key", "privatekey",
    "shared_secret", "sharedsecret", "passphrase", "pass", "pwd",
    "decrypted", "plaintext", "ciphertext", "signature", "hmac",
}

# Keys that are safe to log
SAFE_PARAM_KEYS = {
    "mode", "padding", "algorithm", "encoding", "iterations", "rounds",
    "dklen", "effective_keylen", "key_length", "shift", "rails",
    "matrix_size", "score", "status", "match", "file", "filepath",
    "operation", "encoding", "algo", "method", "category",
}


def _sanitize_params(params: Optional[Dict[str, Any]], include_secrets: bool = False) -> Dict[str, Any]:
    """Remove sensitive parameters from history log.
    
    Args:
        params: Dictionary of parameters
        include_secrets: If True, keep sensitive params (for explicit opt-in)
    
    Returns:
        Sanitized dictionary with only safe parameters
    """
    if not params:
        return {}
    
    if include_secrets:
        return params
    
    sanitized = {}
    for key, value in params.items():
        key_lower = key.lower()
        # Keep if explicitly safe or not in sensitive list
        if key_lower in SAFE_PARAM_KEYS or key_lower not in SENSITIVE_PARAM_KEYS:
            sanitized[key] = value
        else:
            sanitized[key] = "[REDACTED]"
    return sanitized


def get_history_dir() -> Path:
    """Return Path to local history directory."""
    # Place history in the project root or current working directory
    cwd = Path.cwd()
    hist_dir = cwd / HISTORY_DIR_NAME
    return hist_dir


def get_history_file() -> Path:
    """Return Path to history.jsonl file."""
    return get_history_dir() / HISTORY_FILE_NAME


def log_history(
    operation: str,
    input_text: str,
    output_summary: str,
    params: Optional[Dict[str, Any]] = None,
    enabled: bool = True,
    include_secrets: bool = False,
) -> bool:
    """Safely append an operation entry to the history file.

    Args:
        operation: Name of the executed operation (e.g. 'Caesar Brute Force').
        input_text: Original text supplied to the operation.
        output_summary: Summary or main result of the operation.
        params: Optional dictionary of parameters used (e.g. shift, depth).
        enabled: If False, skip logging (honors --no-history flag).
        include_secrets: If True, log sensitive params (default False, requires explicit opt-in).

    Returns:
        True if successfully logged, False if disabled or write failed safely.
    """
    if not enabled:
        return False

    hist_dir = get_history_dir()
    hist_file = get_history_file()

    # Create safe payload, truncating excessively long inputs for privacy & storage
    safe_input = input_text if len(input_text) <= 500 else input_text[:497] + "..."
    safe_output = (
        output_summary
        if len(output_summary) <= 500
        else output_summary[:497] + "..."
    )

    # Sanitize params to remove sensitive data
    safe_params = _sanitize_params(params, include_secrets=include_secrets)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operation": operation,
        "params": safe_params,
        "input": safe_input,
        "output": safe_output,
    }

    try:
        hist_dir.mkdir(parents=True, exist_ok=True)
        with open(hist_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except (OSError, IOError, PermissionError):
        # Gracefully handle write failures without interrupting user operations
        return False


def read_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Read the latest history records from the local history file.

    Args:
        limit: Maximum number of records to return (from newest to oldest).

    Returns:
        List of history record dictionaries.
    """
    hist_file = get_history_file()
    if not hist_file.exists():
        return []

    records: List[Dict[str, Any]] = []
    try:
        with open(hist_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (OSError, IOError, PermissionError):
        return []

    # Return the latest entries up to limit
    return records[-limit:]


def clear_history() -> bool:
    """Safely clear/delete the local history file.

    Returns:
        True if successfully cleared or already nonexistent, False on error.
    """
    hist_file = get_history_file()
    if not hist_file.exists():
        return True

    try:
        hist_file.unlink()
        return True
    except (OSError, IOError, PermissionError):
        return False
