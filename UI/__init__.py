# Re-export start_ui for package-level import
# Use lazy import to avoid importing UI.UI at package import time
# This prevents triggering multiprocessing setup when just importing UI components
def start_ui():
    """Start the UI application"""
    from .UI import start_ui as _start_ui
    return _start_ui()

__all__ = ['start_ui']
