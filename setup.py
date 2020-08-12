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
            'cat_aliases     = imdtk.tools.cat_aliases_cli:main',
            'csv_sink        = imdtk.tools.csv_sink_cli:main',
            'fields_info     = imdtk.tools.fields_info_cli:main',
            'fits_cat_maketable = imdtk.tools.fits_cat_mktbl_sink_cli:main',
            'fits_cat_md     = imdtk.tools.fits_catalog_md_cli:main',
            'fits_headers    = imdtk.tools.fits_headers_cli:main',
            'jwst_oc_calc    = imdtk.tools.jwst_oc_calc_cli:main',
            'jwst_pghybrid_sink = imdtk.tools.jwst_pghybrid_sink_cli:main',
            'jwst_pgsql_sink = imdtk.tools.jwst_pgsql_sink_cli:main',
            'md_pgsql_pipe   = imdtk.tools.md_pgsql_pipe:main',
            'miss_report     = imdtk.tools.miss_report_cli:main',
            'multi_md_pghybrid_pipe = imdtk.tools.multi_md_pghybrid_pipe:main',
            'multi_md_pgsql_pipe    = imdtk.tools.multi_md_pgsql_pipe:main',
            'no_op           = imdtk.tools.nop_cli:main',
            'pickle_sink     = imdtk.tools.pickle_sink_cli:main'
        ]
    },
)
