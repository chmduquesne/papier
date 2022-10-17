import confuse
from sys import stderr

__version__ = '0.0.1'
__author__ = 'Christophe-Marie Duquesne <chmd+papier@chmd.fr>'


class IncludeLazyConfig(confuse.LazyConfig):
    """A version of Confuse's LazyConfig that also merges in data from
    YAML files specified in an `include` setting (stolen from beets)
    """
    def read(self, user=True, defaults=True):
        super().read(user, defaults)

        try:
            for view in self['include']:
                self.set_file(view.as_filename())
        except confuse.NotFoundError:
            pass
        except confuse.ConfigReadError as err:
            stderr.write(f'configuration `include` failed: {err.reason}')


config = IncludeLazyConfig('papier', __name__)
