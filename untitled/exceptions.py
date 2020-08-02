"""Custom exceptions to be caught (usually) in the API blueprint.
"""

class InvalidUsage(Exception):
    """Base exception for when the API was used in the incorrect way
    (i.e. incorrect data, invalid parameters). Will by default have
    a status code of 400 (Bad Request).
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        response = dict(self.payload or ())
        response['error'] = self.message
        return response
