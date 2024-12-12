class SDKException(Exception):
    pass


class ModelNotFoundError(SDKException):
    pass


class InvalidConfigError(SDKException):
    pass


class ConnectionError(SDKException):
    pass


class StreamingError(SDKException):
    pass


class CallbackError(SDKException):
    pass
