"""Basic papier info. Imported before the command line gets parsed"""
import confuse


__version__ = '0.0.1'
__author__ = 'Christophe-Marie Duquesne <chmd+papier@chmd.fr>'


# Plugins which should always be loaded first
core_plugins = ['importer', 'info']


config = confuse.Configuration('papier', __name__)
config.set_env()
