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
            'aliases = imdtk.aliases_cli:main',
            'field_info = imdtk.field_info_cli:main',
            'headers = imdtk.headers_cli:main',
            'oc_calc = imdtk.oc_calc_cli:main'
        ]
    },
)
