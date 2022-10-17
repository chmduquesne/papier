"""Support for papier plugins"""

import logging



# Global logger
log = logging.getLogger('papier')



class PapierPlugin:
    def __init__(self, name=None):
        """Perform one-time plugin setup."""
        self.name = name or self.__module__.split('.')[-1]
        self.config = papier.config[self.name]
