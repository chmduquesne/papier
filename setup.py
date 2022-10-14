import pathlib
from setuptools import setup

here = pathlib.Path(__file__).parent.resolve()

install_requires = (here / 'requirements.txt').read_text(encoding='utf-8').splitlines()

setup(
    name='papier',
    version='0.0.1',
    description='pdf library organizer',
    install_requires=install_requires,
    url='https://github.com/chmduquesne/papier',
    author='Christophe-Marie Duquesne',
    author_email='chmd+papier@chmd.fr',
    license='MIT',
    packages=['papier'],
    entry_points = {
        'console_scripts': ['papier=papier.cli:main'],
    },
    zip_safe=False
    )
