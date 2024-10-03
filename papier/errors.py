"""Papier exceptions"""


class PapierError(Exception):
    """Parent class for all papier related errors"""
    pass


class ConfigError(PapierError):
    """Parent class for all config errors"""
    pass


class CommandError(ConfigError):
    """Config errors related to the command line"""
    pass


class PluginError(PapierError):
    """Errors coming from plugins"""
    pass
