from setuptools import setup, find_packages

setup(
    name='ImdEx',
    version='1.2',
    packages=find_packages(),
    package_data={'imdtk': ['resources/*.txt', 'resources/*.properties']},
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'imdtk_cli = imdtk.cli:main'
        ]
    },
)
