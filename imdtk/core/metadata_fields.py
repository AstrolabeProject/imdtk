#
# Class implementing methods which curate metadata in the field(s)_info structures.
#   Written by: Tom Hicks. 5/1/2020.
#   Last Modified: Call renamed minimal datetime string conversion.
#
import os
import sys
import logging as log

from config.settings import IMAGE_FETCH_PREFIX, IMAGES_DIR
import imdtk.core.fits_utils as fits_utils
from imdtk.core.fields_info_factory import NO_DEFAULT_VALUE

class MetadataFields ():

    def add_default_values_for_fields (self, fields_info):
        """
        Try to instantiate a default value of the correct type for each field in the given
        fields map which does not already have a value.
        """
        for (key, field_info) in fields_info.items():
            if (not field_info.has_value()):
                self.add_default_value_for_a_field(field_info)


    def add_default_value_for_a_field (self, field_info):
        """
        Try to instantiate a default value of the correct type for the given field
        information map which does not already have a value. If found, the value is
        added back to the field information. Ignores field information maps which
        have a "no default value" marker.
        """
        if (field_info.has_value()):        # do not replace existing value
            return                          # exit out now

        default_str = field_info.get('default') # get default string value
        data_type = field_info.get('datatype')  # get data type for the value
        if ( (not default_str) or               # sanity check: need at least value and data type
             (not data_type) or
             (default_str == NO_DEFAULT_VALUE) ): # ignore fields with "no default value" marker
            return                          # exit out now

        value = None                        # variable for extracted value
        try:
            # try to convert the string value to the specified data type
            value = self.string_to_value(default_str, data_type)

        except ValueError:
            obs_core_key = field_info.get('obsCoreKey')
            errMsg = "Unable to convert default value '{0}' for field '{1}' to '{2}'. Field value not set".format(default_str, obs_core_key, data_type)
            log.error("(jwst_processor.add_default_value_for_a_field): {}".format(errMsg))
            value = None                    # signal failure

        except TypeError:
            obs_core_key = field_info.get('obsCoreKey')
            errMsg = "Unknown data type '{0}' for field '{1}'. Field value not set.".format(data_type, obs_core_key)
            log.error("(jwst_processor.add_default_value_for_a_field): {}".format(errMsg))
            value = None                    # signal failure

        if (value is not None):             # if we extracted a value
            field_info.set_value(value)     # then save value in the field info map


    def add_file_information (self, file_path, fields_info):
        """
        Add information about the given input file to the field information map keyed with
        a special keyword that is shared with other modules.
        """
        if (self._DEBUG):
            print("(jwst_processor.add_file_information): Adding file info for '{}'".format(file_path))

        fname_info = fields_info.get('file_name')
        if (fname_info is not None):
            fname_info.set_value(os.path.basename(file_path))

        fpath_info = fields_info.get('file_path')
        if (fpath_info is not None):
            fpath_info.set_value(os.path.abspath(file_path))

        # estimated size is the size of the file
        fsize_info = fields_info.get('access_estsize')
        if (fsize_info is not None):
            fsize_info.set_value(os.path.getsize(file_path))


    def add_info_from_fits_headers (self, header_fields, fields_info):
        """
        For the given map of FITS file header fields, find the corresponding ObsCore keyword,
        if any, and lookup the field information for that key. If found, add the corresponding
        FITS file header keyword and value string.
        """
        if (self._DEBUG):
            print("(jwst_processor.add_info_from_fits_headers): header_fields: {}".format(header_fields))
        for hdr_key, hdr_value_str in header_fields.items():
            # map header key string to ObsCore key string (resolve aliases)
            obs_core_key = self.get_obs_core_key_from_alias(hdr_key)
            if (obs_core_key):                                   # if found alias mapping
                field_info = fields_info.get(obs_core_key)
                if (field_info):            # if we have this ObsCore field, add header info
                    field_info.update({'hdrKey': hdr_key, 'hdrValueStr': hdr_value_str})


    def calc_corners (self, wcs_info, fields_info):
        """
        Calculate the corner points and spatial limits for the current image,
        given the FITS file WCS information and the field information map.

        The calculated corners and limits are stored in the given field information map.
        """
        corners = fits_utils.get_image_corners(wcs_info)
        if (len(corners) == 4):
            self.set_corner_field(fields_info, 'im_ra1', 'im_dec1', corners[0]) # LowerLeft
            self.set_corner_field(fields_info, 'im_ra2', 'im_dec2', corners[1]) # UpperLeft
            self.set_corner_field(fields_info, 'im_ra3', 'im_dec3', corners[2]) # UpperRight
            self.set_corner_field(fields_info, 'im_ra4', 'im_dec4', corners[3]) # LowerRight

        # now use the corners to calculate the min/max spatial limits of the image
        self.calc_spatial_limits(corners, fields_info)


    def calc_pixtype (self, header_fields, fields_info):
        """
        Calculate the value string for the ObsCore im_pixeltype field based on the value
        of the FITS BITPIX keyword.
        """
        bitpix = header_fields.get('BITPIX')
        pixtype_info = fields_info.get('im_pixtype')
        if (bitpix and pixtype_info):
            pixtype_info.set_value(fits_utils.lookup_pixtype(bitpix))


    def calc_scale (self, wcs_info, fields_info):
        """
        Calculate the scale for the current image using the given
        given the FITS file WCS information and the field information map.

        Since only the first scale value is used, this method assumes square pixels.

        The units of the scale are the same as the units of cdelt,
        crval, and cd for the celestial WCS and can be obtained by inquiring the
        value of cunit property of the input WCS object.

        The calculated scale is stored in the given field information map.
        """
        scale = fits_utils.get_image_scale(wcs_info)
        field_info = fields_info.get('im_scale')
        if ((field_info is not None) and (len(scale) > 0)):
            field_info.set_value(scale[0])


    def calc_spatial_limits (self, corners, fields_info):
        """
        Calculate the min/max of the RA and DEC axes. This method must be called after
        the image corners are computed, since it relies on those values.
        """
        lo1_info  = fields_info.get('spat_lolimit1')
        hi1_info  = fields_info.get('spat_hilimit1')
        lo2_info  = fields_info.get('spat_lolimit2')
        hi2_info  = fields_info.get('spat_hilimit2')

        # sanity check: check that all spatial limit variables exist
        if (lo1_info is not None and hi1_info is not None and
            lo2_info is not None and hi2_info is not None):
            ras = list(map(lambda c: c[0], corners))
            decs = list(map(lambda c: c[1], corners))

            lo1_info.set_value(min(ras))
            hi1_info.set_value(max(ras))
            lo2_info.set_value(min(decs))
            hi2_info.set_value(max(decs))


    def calc_wcs_coords (self, wcs_info, header_fields, fields_info):
        """
        Extract the WCS coordinates for the reference pixel of the current image file.
        Sets both s_ra and s_dec fields simultaneously when either field is processed.
        This method assumes that neither s_ra nor s_dec fields have a value yet and it will
        overwrite current values for both s_ra and s_dec if that assumption is not valid.
        """
        ra_info  = fields_info.get('s_ra')  # get s_ra entry
        dec_info = fields_info.get('s_dec') # get s_dec entry

        crval = list(wcs_info.wcs.crval)
        ctype = list(wcs_info.wcs.ctype)

        if (ra_info and dec_info and            # sanity check vars
            (len(crval) > 1) and (len(ctype) > 1)):
            if (ctype[0].startswith('RA')):     # if CRVAL1 has the RA value
                ra_info.set_value(crval[0])     # put CRVAL1 value into s_ra
                dec_info.set_value(crval[1])    # put CRVAL2 value into s_dec
            elif (ctype[0].startswith('DEC')):  # if CRVAL1 has the DEC value
                dec_info.set_value(crval[0])    # put CRVAL1 value into s_dec
                ra_info.set_value(crval[1])     # put CRVAL2 value into s_ra
            else:
                errMsg = "(metadata_fields.calc_wcs_coords): Unable to assign RA/DEC axes from ctype={}".format(ctype)
                log.error(errMsg)


    def compute_values_for_fields (self, wcs_info, header_fields, fields_info):
        """
        Try to compute a value of the correct type for each field, in the
        given field maps, which does not already have a value.
        """

        # ////////////////////////////////////////////////////////////////////////////////
        #  NOTE: SPECIAL CASE: correct the t_exptime zero value
        #         with a default of 1347.0 per Eiichi Egami 20190626.
        #         Remove this code when the t_exptime field gets real values in the future.
        t_exptime = fields_info.get_value_for('t_exptime')
        if (t_exptime == 0.0):
            fields_info.set_value_for('t_exptime', 1347.0)
        # ////////////////////////////////////////////////////////////////////////////////

        # special case: If given a collection name argument, then use it
        collection = self._args.get('collection')
        if (collection):
            fields_info.set_value_for('obs_collection', collection)

        # general case: compute values for fields which do not already have a value
        for (key, field_info) in fields_info.items():
            if (not field_info.has_value()):   # do not replace existing values
                self.compute_value_for_a_field(field_info, wcs_info, header_fields, fields_info)


    def compute_value_for_a_field (self, field_info, wcs_info, header_fields, fields_info):
        """
        Try to compute a value of the correct type for the given field information
        map which does not already have a value. If successful, the value is added back
        to the field information. The map containing all fields is also passed to this method
        to enable calculations based on the values of other fields.
        """
        if (field_info.has_value()):        # do not replace existing values
            return                          # exit out now

        obs_core_key = field_info.get('obsCoreKey')

        if (obs_core_key in ['s_ra', 's_dec']): # coordinate fields extracted from the file
            self.calc_wcs_coords(wcs_info, header_fields, fields_info)

        elif (obs_core_key in  ['im_naxis1', 'im_naxis2']):
            fields_info.copy_value('s_xel1', 'im_naxis1') # s_xel1 already filled by aliasing
            fields_info.copy_value('s_xel2', 'im_naxis2') # s_xel2 already filled by aliasing

        elif (obs_core_key == 's_resolution'):
            self.calc_spatial_resolution(fields_info)

        elif (obs_core_key == 'im_pixtype'):
            self.calc_pixtype(header_fields, fields_info)

        elif (obs_core_key == 'access_url'):
            # filename = fields_info.get_value_for('file_name')
            file_path = fields_info.get_value_for('file_path')
            if (file_path is not None):
                image_path = "{0}{1}{2}".format(IMAGE_FETCH_PREFIX, IMAGES_DIR, file_path)
                field_info.set_value(image_path)

        elif (obs_core_key == 'instrument_name'):
            # create instrument name from NIRCam + MODULE value
            module = fields_info.get_value_for('nircam_module')
            inst_name = "NIRCam-{}".format(module) if (module is not None) else "NIRCam"
            field_info.set_value(inst_name)

        elif (obs_core_key == 'target_name'):
            filename = fields_info.get_value_for('file_name')
            if (filename is not None):
                if (filename.lower().startswith("goods_s")):
                    field_info.set_value("goods_south")
                elif (filename.lower().startswith("goods_n")):
                    field_info.set_value("goods_north")
                else:
                    field_info.set_value("UNKNOWN")


    def convert_header_values (self, fields_info):
        """
        Try to convert the header value string in each field information entry to the
        correct type (as specified in the field info entry).
        If successful, the converted value is added back to the corresponding field information.
        """
        for (key, field_info) in fields_info.items():
            self.convert_a_header_value(field_info)


    def convert_a_header_value (self, field_info):
        """
        Try to create a value of the correct type for the given field information map.
        Tries to convert the header value string to the proper data type. If successful,
        the value is added back to the field information.
        """
        value_str = field_info.get('hdrValueStr') # string value for header keyword
        data_type = field_info.get('datatype')    # data type for the value
        if ((value_str is None) or                # sanity check: need at least value and data type
            (not data_type)):
            return                          # exit out now

        value = None                        # variable for extracted value
        try:
            # try to convert the string value to the specified data type
            value = self.string_to_value(value_str, data_type)

        except ValueError:
            fits_key = field_info.get('hdrKey') # header key from FITS file
            errMsg = "Unable to convert value '{0}' for field '{1}' to '{2}'. Ignoring bad field value.".format(value_str, fits_key, data_type)
            log.error("(MetadataFields.convert_a_header_value): {}".format(errMsg))
            value = None                    # signal failure

        except TypeError:
            fits_key = field_info.get('hdrKey') # header key from FITS file
            errMsg = "Unknown data type '{0}' for field '{1}'. Ignoring bad field value.".format(data_type, fits_key)
            log.error("(MetadataFields.convert_a_header_value): {}".format(errMsg))
            value = None                    # signal failure

        if (value is not None):             # if we extracted a value
            field_info.set_value(value)     # then save value in the field info map


    def ensure_required_fields (self, fields_info):
        """ Find and report ObsCore fields with still have no value. """
        for (key, field_info) in fields_info.items():
            obs_core_key = field_info.get('obsCoreKey')
            if (obs_core_key and not field_info.has_value()): # if ObsCore and has no value
                req_fld = 'Required' if field_info.get('required') else 'Optional'
                if (self._VERBOSE or self._DEBUG):
                    errMsg = "(MetadataFields.ensure_required_fields): {0} field '{1}' still does not have a value.".format(req_fld, obs_core_key)
                    # log.warning(errMsg)
                    print('WARNING: ' + errMsg)


    def set_corner_field (self, fields_info, ra_field_key, dec_field_key, corner):
        """
        Store the given corner coordinates [RA, DEC] into the corner fields named by
        the given RA field keyword and DEC field keyword, respectively.
        """
        if (len(corner) > 1):               # each corner is a list of RA, DEC
            fields_info.set_value_for(ra_field_key, corner[0])
            fields_info.set_value_for(dec_field_key, corner[1])


    def string_to_value (self, value_str, data_type):
        """
        Convert the given string value to the given data type. Allowed data type specifiers
        are limited to: "date", "double", "float", "integer", and "string".

        :raises TypeError for illegal data type specifier
        :raises ValueError if value conversion fails
        """
        if (self._DEBUG):
            print("(IFitsFileProcessor.string_to_value): value_str='{0}', data_type='{1}".format(value_str, data_type))

        if (not value_str or not data_type):  # sanity check: need at least value and datatype
            return None                       # exit out now

        value = None                        # return variable for extracted value
        try:                                # dispatch conversions on the datatype
            if (data_type == 'integer'):
                value = int(value_str)
            elif ((data_type == 'double') or (data_type == 'float')):
                value = float(value_str)
            elif (data_type == 'string'):
                value = str(value_str)
            elif (data_type == 'date'):          # this one conversion is FITS dependent
                value = fits_utils.fits_utc_date(value_str)  # FITS date = ISO-8601 w/o the trailing Z
            else:
                raise TypeError("Unknown datatype '{}' specified for conversion".format(data_type))

        except ValueError:
            raise ValueError("Unable to convert value '{}' to '{}'".format(value_str, data_type))

        return value                        # return the converted value
