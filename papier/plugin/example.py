"""example papier plugin"""
import papier.plugins


def on_plugins_loaded():
    print('all plugins loaded')


papier.plugins.register_listener('plugins loaded', on_plugins_loaded)
