"""Basic papier info. Imported before the command line gets parsed"""
import confuse
from .extractor import extracts, extractors
from .document import Document
from .errors import PapierError, ConfigError, CommandError, PluginError


__all__ = ['extracts', 'extractors', 'Document', 'PapierError',
           'ConfigError', 'CommandError', 'PluginError']
__version__ = '0.0.1'
__author__ = 'Christophe-Marie Duquesne <chmd+papier@chmd.fr>'


# Plugins which should always be loaded first
core_plugins = ['importer', 'info', 'organize', 'set_tags']


config = confuse.Configuration('papier', __name__)
config.set_env()
