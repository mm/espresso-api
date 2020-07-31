"""Custom exceptions to be caught (usually) in the API blueprint.
"""

class URLInvalidError(Exception):
    """Raised when a URL isn't valid. An invalid URL in this context
    is any URL not starting with http:// or https://.
    """
    pass
