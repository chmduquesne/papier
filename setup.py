from setuptools import setup

setup(name='papier',
    version='0.0.1',
    description='pdf library organizer',
    url='https://github.com/chmduquesne/papier',
    author='Christophe-Marie Duquesne',
    author_email='chmd+papier@chmd.fr',
    license='MIT',
    packages=['papier'],
    entry_points = {
        'console_scripts': ['papier=papier.cli:main'],
    },
    zip_safe=False)
