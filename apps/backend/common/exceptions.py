class TCMSException(Exception):
    default_message = "An application error occurred."

    def __init__(self, message: str | None = None, *, code: str | None = None):
        self.message = message or self.default_message
        self.code = code
        super().__init__(self.message)


class TCMSValidationError(TCMSException):
    default_message = "Validation failed."


class TCMSPermissionDenied(TCMSException):
    default_message = "Permission denied."


class TCMSNotFound(TCMSException):
    default_message = "Requested resource was not found."


class TCMSConflict(TCMSException):
    default_message = "The request conflicts with the current resource state."


class TCMSConfigurationError(TCMSException):
    default_message = "Application configuration is invalid."
