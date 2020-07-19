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
            'aliases         = imdtk.tools.aliases_cli:main',
            'csv_sink        = imdtk.tools.csv_sink_cli:main',
            'fields_info     = imdtk.tools.fields_info_cli:main',
            'fits_headers    = imdtk.tools.fits_headers_cli:main',
            'fits_table      = imdtk.tools.fits_table_cli:main',
            'jwst_oc_calc    = imdtk.tools.jwst_oc_calc_cli:main',
            'jwst_pghybrid_sink = imdtk.tools.jwst_pghybrid_sink_cli:main',
            'jwst_pgsql_sink = imdtk.tools.jwst_pgsql_sink_cli:main',
            'md_pgsql_pipe   = imdtk.tools.md_pgsql_pipe:main',
            'miss_report     = imdtk.tools.miss_report_cli:main',
            'multi_md_pgsql_pipe = imdtk.tools.multi_md_pgsql_pipe:main',
            'no_op           = imdtk.tools.nop_cli:main',
            'pickle_sink     = imdtk.tools.pickle_sink_cli:main'
        ]
    },
)
