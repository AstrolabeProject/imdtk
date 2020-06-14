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
            'fields_info = imdtk.fields_info_cli:main',
            'headers = imdtk.headers_cli:main',
            'jwst_oc_calc = imdtk.jwst_oc_calc_cli:main',
            'miss_report = imdtk.miss_report_cli:main'
        ]
    },
)
