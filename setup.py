from setuptools import setup, find_packages

setup(
    name='ImdTk',
    version='0.1',
    packages=find_packages(),
    package_data={'imdtk': ['resources/*.txt', 'resources/*.properties']},
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'headers = imdtk.headers_cli:main',
            'aliases = imdtk.aliases_cli:main'
        ]
    },
)
