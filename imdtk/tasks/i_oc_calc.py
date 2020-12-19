#
# Class to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/14/2020.
#   Last Modified: Refactor to allow abstract calc and default setting methods.
#
import abc

from imdtk.tasks.i_task import IImdTask
import imdtk.tasks.metadata_utils as md_utils
import imdtk.tasks.oc_calc_utils as occ_utils


class IObsCoreCalcTask (IImdTask):
    """ Class to calculate values for ObsCore fields in a metadata structure. """

    @abc.abstractmethod
    def calc_access_url (self, metadata, calculations):
        """ Use the given metadata to create the URL to fetch the file from the server. """
        pass


    @abc.abstractmethod
    def calc_instrument_name (self, metadata, calculations):
        """ Use the given metadata to create re/create an instrument name. """
        pass


    @abc.abstractmethod
    def calc_spatial_resolution (self, metadata, calculations):
        """
        Use the filter value to determine the spatial resolution based on the given
        filter-resolution table.
        """
        pass


    @abc.abstractmethod
    def set_default_instrument_name (self, defaults, metadata, calculations):
        """ Use the given metadata to create create a default instrument name. """
        pass


    @abc.abstractmethod
    def set_default_target_name (self, defaults, metadata, calculations):
        """ Use the given metadata to create create a default target name. """
        pass


    def __init__(self, args):
        """
        Constructor for class which calculates values for ObsCore fields in a metadata structure.
        """
        super().__init__(args)



    #
    # Non-interface and/or task-specific Methods
    #

    def calculate_results (self, wcs_info, metadata):
        """
        Try to produce a value for each of the fields desired in the results.
        Values are extracted, calculated, or defaulted from existing metadata.
        Return a dictionary of fields and values for all fields for which
        a value was able to be produced.
        """
        calculations = dict()               # structure for calculated results

        # calculate some initial values from the FITS file WCS information
        occ_utils.calc_scale(wcs_info, calculations)
        occ_utils.calc_corners(wcs_info, calculations)

        # copy any file information fields to results
        occ_utils.copy_file_info(metadata, calculations)

        # copy any FITS header fields that were aliased to desired result fields
        occ_utils.copy_aliased(metadata, calculations)

        # calculate any values which require special casing
        self.calc_special_case_fields(wcs_info, metadata, calculations)

        # try to produce a value for each desired field
        self.calc_field_values(wcs_info, metadata, calculations)

        return calculations


    def calc_field_values (self, wcs_info, metadata, calculations):
        """
        For all desired fields, compute (or recompute) a value for each field.
        Values are extracted, calculated, or defaulted from existing metadata.
        If a value is produced for a field, store the field and its value into
        the given calculations structure.
        """
        defaults = md_utils.get_defaults(metadata)  # get defaults once

        # make a list of the desired fields (as listed in the fields info file)
        fields_info = md_utils.get_fields_info(metadata)
        desired = fields_info.keys() if fields_info else []

        # try to calculate a value for each desired field
        for field_name in desired:
            self.calc_field_value(field_name, defaults, wcs_info, metadata, calculations)
            if (field_name not in calculations):  # if field still has no value
                self.set_default_value(field_name, defaults, wcs_info, metadata, calculations)


    def calc_field_value (self, field_name, defaults, wcs_info, metadata, calculations):
        """
        Provide the opportunity to calculate (or recalculate) a value for the named field.
        This version may call abstract methods which call down to the concrete methods.
        """
        if (field_name in ['s_ra', 's_dec']):
            occ_utils.calc_wcs_coordinates(wcs_info, calculations)

        elif (field_name in ['im_naxis1', 'im_naxis2']):
            if (calculations.get('s_xel1') is not None):
                calculations['im_naxis1'] = calculations.get('s_xel1')
            if (calculations.get('s_xel2') is not None):
                calculations['im_naxis2'] = calculations.get('s_xel2')

        elif (field_name == 's_resolution'):
            self.calc_spatial_resolution(calculations)

        elif (field_name == 'im_pixtype'):
            occ_utils.calc_pixtype(metadata, calculations)

        elif (field_name in ['access_estsize', 'file_size']):
            occ_utils.calc_access_estsize(metadata, calculations)

        elif (field_name == 'access_url'):
            self.calc_access_url(metadata, calculations)


    def set_default_value (self, field_name, defaults, wcs_info, metadata, calculations):
        """
        Final effort to calculate or set a fallback/default value for the named field.
        This version may call abstract methods which call down to child concrete methods.
        """
        if (field_name == 'target_name'):
            self.set_default_target_name(defaults, metadata, calculations)

        elif (field_name == 'instrument_name'):
            self.set_default_instrument_name(defaults, metadata, calculations)

        # if field still has no value, try to set a default from the fields info
        if (field_name not in calculations):
            occ_utils.set_default(field_name, defaults, calculations)
