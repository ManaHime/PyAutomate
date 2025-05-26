"""
Debug module for PyAutomate.
Provides centralized control over debug output and logging functionality.
"""

# Global debug state
_debug_mode = False
_log_level = 1  # 1: basic, 2: detailed, 3: verbose

def set_debug_mode(enabled: bool, level: int = 1):
    """
    Enable or disable debug mode and set log level.
    
    Args:
        enabled: Whether to enable debug output
        level: Log level (1: basic, 2: detailed, 3: verbose)
    """
    global _debug_mode, _log_level
    _debug_mode = enabled
    _log_level = max(1, min(3, level))  # Clamp between 1 and 3

def get_debug_mode() -> bool:
    """Get current debug mode state."""
    return _debug_mode

def get_log_level() -> int:
    """Get current log level."""
    return _log_level

def debug_print(*args, level: int = 1, **kwargs):
    """
    Print debug message if debug mode is enabled and message level is sufficient.
    
    Args:
        *args: Message to print
        level: Minimum log level required to show this message (1: basic, 2: detailed, 3: verbose)
        **kwargs: Additional print arguments
    """
    if _debug_mode and level <= _log_level:
        print(*args, **kwargs)

# Convenience functions for different log levels
def basic_print(*args, **kwargs):
    """Print basic debug message (level 1)."""
    debug_print(*args, level=1, **kwargs)

def detailed_print(*args, **kwargs):
    """Print detailed debug message (level 2)."""
    debug_print(*args, level=2, **kwargs)

def verbose_print(*args, **kwargs):
    """Print verbose debug message (level 3)."""
    debug_print(*args, level=3, **kwargs) 