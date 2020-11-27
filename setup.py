from setuptools import setup, find_packages

setup(
    name='ImdTk',
    version='0.19.0',
    packages=find_packages(),
    package_data={'imdtk': ['resources/*.txt', 'resources/*.properties']},
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'cat_aliases     = imdtk.tools.catalog_aliases_cli:main',
            'csv_sink        = imdtk.tools.csv_file_sink_cli:main',
            'fields_info     = imdtk.tools.fields_info_cli:main',
            'fits_cat_data   = imdtk.tools.fits_catalog_data_cli:main',
            'fits_cat_fill   = imdtk.tools.fits_catalog_table_sink_cli:main',
            'fits_cat_md     = imdtk.tools.fits_catalog_md_cli:main',
            'fits_cat_mktbl  = imdtk.tools.fits_catalog_mktbl_sink_cli:main',
            'fits_img_md     = imdtk.tools.fits_image_md_cli:main',
            'img_aliases     = imdtk.tools.image_aliases_cli:main',
            'irods_fits_cat_md  = imdtk.tools.irods_fits_catalog_md_cli:main',
            'irods_fits_img_md  = imdtk.tools.irods_fits_image_md_cli:main',
            'irods_jwst_oc_calc = imdtk.tools.irods_jwst_oc_calc_cli:main',
            'jwst_oc_calc    = imdtk.tools.jwst_oc_calc_cli:main',
            'jwst_pghyb_sink = imdtk.tools.jwst_pghybrid_sink_cli:main',
            'jwst_pgsql_sink = imdtk.tools.jwst_pgsql_sink_cli:main',
            'miss_report     = imdtk.tools.miss_report_cli:main',
            'no_op           = imdtk.tools.nop_cli:main',
            'pickle_sink     = imdtk.tools.pickle_sink_cli:main',
            'fits_cat_mktbl_pipe  = imdtk.tools.fits_catalog_mktbl_pipe:main',
            'fits_cat_table_pipe  = imdtk.tools.fits_catalog_table_pipe:main',
            'irods_md_pghyb_pipe  = imdtk.tools.irods_md_pghybrid_pipe:main',
            'irods_md_pgsql_pipe  = imdtk.tools.irods_md_pgsql_pipe:main',
            'irods_mmd_pghyb_pipe = imdtk.tools.irods_mmd_pghybrid_pipe:main',
            'irods_mmd_pgsql_pipe = imdtk.tools.irods_mmd_pgsql_pipe:main',
            'md_pghyb_pipe   = imdtk.tools.md_pghybrid_pipe:main',
            'md_pgsql_pipe   = imdtk.tools.md_pgsql_pipe:main',
            'mmd_pghyb_pipe  = imdtk.tools.mmd_pghybrid_pipe:main',
            'mmd_pgsql_pipe  = imdtk.tools.mmd_pgsql_pipe:main'
        ]
    },
)
