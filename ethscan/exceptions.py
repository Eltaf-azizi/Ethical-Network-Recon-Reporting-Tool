"""Custom exception types for ethscan."""


class EthScanError(Exception):
    """Base class for all ethscan errors."""


class AuthorizationError(EthScanError):
    """Raised when the authorization gate refuses to run."""


class ScopeError(EthScanError):
    """Raised when a scope file is missing, malformed, or too narrow."""


class PortSpecError(EthScanError):
    """Raised when a port spec string can't be parsed."""