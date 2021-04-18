"""Signals used throughout the application for async task processing and notifications.
"""

from blinker import Namespace

espresso_signals = Namespace()

link_created = espresso_signals.signal("link-created")
