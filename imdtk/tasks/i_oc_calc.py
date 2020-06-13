#
# Class to calculate values for the ObsCore fields in a FITS-derived metadata structure.
#   Written by: Tom Hicks. 6/14/2020.
#   Last Modified: Split from JWST-specific class to create abstract parent interface.
#
import os, sys
import abc

from imdtk.tasks.i_task import IImdTask
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
    def calc_target_name (self, metadata, calculations):
        """ Use the given metadata to create re/create a target name. """
        pass


    def __init__(self, args):
        """
        Constructor for class which calculates values for ObsCore fields in a metadata structure.
        """
        pass                                # currently no initialization needed



    #
    # Non-interface and/or Task-specific Methods
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
        defaults = occ_utils.get_defaults(metadata)
        fields_info = occ_utils.get_fields_info(metadata)

        # make list of desired fields
        desired = fields_info.keys() if fields_info else []
        for fieldname in desired:
            self.calc_field_value(fieldname, wcs_info, metadata, calculations)
            if (fieldname not in calculations): # if field still has no value
                occ_utils.set_default(fieldname, defaults, calculations)


    def calc_field_value (self, field_name, wcs_info, metadata, calculations):
        """
        Provide the opportunity to calculate (or recalculate) a value for the named field.
        This version calls abstract methods which call down to the child concrete methods.
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

        elif (field_name == 'access_url'):
            self.calc_access_url(metadata, calculations)

        elif (field_name == 'instrument_name'):
            self.calc_instrument_name(metadata, calculations)

        elif (field_name == 'target_name'):
            self.calc_target_name(metadata, calculations)
