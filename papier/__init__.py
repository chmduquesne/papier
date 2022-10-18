import confuse
from sys import stderr


__version__ = '0.0.1'
__author__ = 'Christophe-Marie Duquesne <chmd+papier@chmd.fr>'


default_plugins = ['basics']


config = confuse.Configuration('papier', __name__)
config.set_env()
