from setuptools import setup, find_packages

setup(
    name='ImdTk',
    version='0.7.0',
    packages=find_packages(),
    package_data={'imdtk': ['resources/*.txt', 'resources/*.properties']},
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'aliases         = imdtk.aliases_cli:main',
            'csv_sink        = imdtk.csv_sink_cli:main',
            'fields_info     = imdtk.fields_info_cli:main',
            'fits_headers    = imdtk.fits_headers_cli:main',
            'fits_table      = imdtk.fits_table_cli:main',
            'jwst_oc_calc    = imdtk.jwst_oc_calc_cli:main',
            'jwst_pghybrid_sink = imdtk.jwst_pghybrid_sink_cli:main',
            'jwst_pgsql_sink = imdtk.jwst_pgsql_sink_cli:main',
            'miss_report     = imdtk.miss_report_cli:main',
            'no_op           = imdtk.nop_cli:main',
            'pickle_sink     = imdtk.pickle_sink_cli:main'
        ]
    },
)
