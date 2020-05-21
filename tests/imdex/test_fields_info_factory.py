# Tests of fields info factory class.
#   Written by: Tom Hicks. 4/10/2020.
#   Last Modified: Update tests for no output directory argument.
#
from imdtk.core.field_info import FieldInfo
from imdtk.core.fields_info import FieldsInfo
from imdtk.core.fields_info_factory import FieldsInfoFactory

import os
import pytest


class TestFieldInfo(object):

    def test_get_value (self):
        fi = FieldInfo()
        assert fi.get_value() is None

        fi = FieldInfo({'wrong_Key': 'never retrieved'})
        assert fi.get_value() is None

        fi = FieldInfo({'_value': 'a stored value'})
        val = fi.get_value()
        assert val == 'a stored value'


    def test_has_value (self):
        fi = FieldInfo()
        assert fi.has_value() == False

        fi = FieldInfo({'BAD_Key': 'never found'})
        assert fi.has_value() == False

        fi = FieldInfo({'_value': 'a stored value'})
        assert fi.has_value() == True


    def test_set_value (self):
        fi = FieldInfo()
        assert fi.has_value() == False

        fi.set_value('SOME VALUE')
        assert fi.has_value() == True
        assert fi.get_value() == 'SOME VALUE'



class TestFieldsInfo(object):

    def test_get_value_for_empty (self):
        fis = FieldsInfo()
        assert fis.get_value_for('') is None
        assert fis.get_value_for('key') is None
        assert fis.get_value_for('field') is None
        assert fis.get_value_for('aValue') is None
        assert fis.get_value_for('ANY') is None


    def test_get_value_for (self):
        fi2 = FieldInfo()
        fi2.set_value('aValue')
        fi3 = FieldInfo()
        fi3.set_value('VALUE')

        fis = FieldsInfo({'FI2': fi2, 'FI3': fi3})

        assert fis.get_value_for('') is None
        assert fis.get_value_for('key') is None
        assert fis.get_value_for('aValue') is None
        assert fis.get_value_for('fi2') is None

        assert fis.get_value_for('FI2') == 'aValue'
        assert fis.get_value_for('FI3') == 'VALUE'


    def test_get_other_properties (self):
        fi2 = FieldInfo()
        fi2.set_value('aValue')
        fi2['other'] = 'other prop'        # field info objects will have other properties too
        fi2['more'] = 'property2'          # field info objects will have other properties too

        fis = FieldsInfo({'FI2': fi2})

        assert fis.get_value_for('') is None
        assert fis.get_value_for('aValue') is None
        assert fis.get_value_for('fi2') is None
        assert fis.get_value_for('other') is None

        assert fis.get_value_for('FI2') == 'aValue'
        assert fis.get('FI2').get('other') == 'other prop'
        assert fis.get('FI2').get('more') == 'property2'


    def test_has_value_for_empty (self):
        fis = FieldsInfo()
        assert fis.has_value_for('') == False
        assert fis.has_value_for('ANY') == False
        assert fis.has_value_for('key') == False
        assert fis.has_value_for('aValue') == False


    def test_has_value_for (self):
        fi2 = FieldInfo()
        fi2.set_value('aValue')
        fi3 = FieldInfo()
        fi3.set_value('VALUE')

        fis = FieldsInfo({'aKey': fi2, 'KEY': fi3})

        assert fis.has_value_for('AKEY') == False
        assert fis.has_value_for('key') == False
        assert fis.has_value_for('VALUE') == False

        assert fis.has_value_for('aKey') == True
        assert fis.has_value_for('KEY') == True


    def test_set_value_for_fails (self):
        fi1 = FieldInfo()
        fi1.set_value('SOME VALUE')

        fis = FieldsInfo()                  # create empty fields info
        assert fis.has_value_for('aKey') == False

        fis.set_value_for('aKey', fi1)      # no existing keyed field, so nothing is set!
        assert fis.has_value_for('aKey') == False     # still not set
        assert fis.get_value_for('aKey') is None      # so no value to get


    def test_set_value_for (self):
        fi1 = FieldInfo()
        fi1.set_value('SOME VALUE')
        fi2 = FieldInfo()
        fi2.set_value('aValue')

        fis = FieldsInfo({'aKey': fi2})
        assert fis.has_value_for('aKey') == True
        assert fis.get_value_for('aKey') == 'aValue'
        assert fis.get_value_for('aKey') != 'SOME VALUE'

        fis.set_value_for('aKey', 'SOME VALUE')
        assert fis.has_value_for('aKey') == True
        assert fis.get_value_for('aKey') != 'aValue'
        assert fis.get_value_for('aKey') == 'SOME VALUE'


    def test_put (self):
        """ test normal dictionary put method. """
        fi1 = FieldInfo()                   # field info with only special value
        fi1.set_value('value1')

        fi2 = FieldInfo()
        fi2.set_value('value2')             # field info with special value and
        fi2['other'] = 'other prop'         # field info objects will have other properties too
        fi2['more'] = 'property2'           # field info objects will have other properties too

        fis = FieldsInfo()                  # create empty fields info
        assert fis.has_value_for('aKey') == False

        fis['aKey'] = fi1                   # add first field info
        assert len(fis) == 1
        assert fis.has_value_for('aKey') == True
        assert fis.get_value_for('aKey') != 'aKey'
        assert fis.get_value_for('aKey') != fi1
        assert fis.get_value_for('aKey') == 'value1'

        fis['KEY2'] = fi2                   # add second field info
        assert len(fis) == 2
        assert fis.has_value_for('KEY2') == True
        assert fis.get_value_for('KEY2') != 'aKey'
        assert fis.get_value_for('KEY2') != fi1
        assert fis.get_value_for('KEY2') != 'value1'
        assert fis.get_value_for('KEY2') != 'KEY2'
        assert fis.get_value_for('KEY2') != fi2
        assert fis.get_value_for('KEY2') == 'value2'


    def test_copy_value_empty (self):
        fis = FieldsInfo()
        assert fis.has_value_for('fromKey') == False
        assert fis.has_value_for('toKey') == False

        fis.copy_value('fromKey', 'toKey')
        assert fis.has_value_for('fromKey') == False
        assert fis.has_value_for('toKey') == False


    def test_copy_value_FromNoTo (self):
        fi2 = FieldInfo()
        fi2.set_value('aValue')

        fis = FieldsInfo({'fromKey': fi2})
        assert fis.has_value_for('fromKey') == True
        assert fis.get_value_for('fromKey') == 'aValue'
        assert fis.has_value_for('toKey') == False
        fis.copy_value('fromKey', 'toKey')
        assert fis.has_value_for('fromKey') == True         # still has value
        assert fis.get_value_for('fromKey') == 'aValue'     # value unaltered
        assert fis.has_value_for('toKey') == False          # still has no value


    def test_copy_value_FromTo (self):
        fi1 = FieldInfo()
        fi1.set_value('OLD VALUE')
        fi2 = FieldInfo()
        fi2.set_value('new value')

        fis = FieldsInfo({'fromKey': fi2, 'toKey': fi1})
        assert fis.has_value_for('fromKey') == True
        assert fis.get_value_for('fromKey') == 'new value'
        assert fis.has_value_for('toKey') == True
        assert fis.get_value_for('toKey') == 'OLD VALUE'

        fis.copy_value('fromKey', 'toKey')
        assert fis.has_value_for('fromKey') == True         # still has value
        assert fis.get_value_for('fromKey') == 'new value'  # value unaltered
        assert fis.has_value_for('toKey') == True           # still has value
        assert fis.get_value_for('toKey') == 'new value'    # value changed


    def test_copy_value_FromToOverwrite (self):
        fi1 = FieldInfo()
        fi1.set_value('TARGET')
        fi2 = FieldInfo()
        fi2.set_value('SOURCE')

        fis = FieldsInfo({'fromKey': fi2, 'toKey': fi1})
        assert fis.has_value_for('fromKey') == True
        assert fis.get_value_for('fromKey') == 'SOURCE'
        assert fis.has_value_for('toKey') == True
        assert fis.get_value_for('toKey') == 'TARGET'

        fis.copy_value('fromKey', 'toKey', overwrite=True)
        assert fis.has_value_for('fromKey') == True         # still has value
        assert fis.get_value_for('fromKey') == 'SOURCE'     # value unaltered
        assert fis.has_value_for('toKey') == True           # still has value
        assert fis.get_value_for('toKey') == 'SOURCE'       # value changed


    def test_copy_value_FromToNoOverwrite (self):
        fi1 = FieldInfo()
        fi1.set_value('TOVALUE')
        fi2 = FieldInfo()
        fi2.set_value('FROMVAL')

        fis = FieldsInfo({'fromKey': fi2, 'toKey': fi1})
        assert fis.has_value_for('fromKey') == True
        assert fis.get_value_for('fromKey') == 'FROMVAL'
        assert fis.has_value_for('toKey') == True
        assert fis.get_value_for('toKey') == 'TOVALUE'

        fis.copy_value('fromKey', 'toKey', overwrite=False)
        assert fis.has_value_for('fromKey') == True         # still has value
        assert fis.get_value_for('fromKey') == 'FROMVAL'    # value unaltered
        assert fis.has_value_for('toKey') == True           # still has value
        assert fis.get_value_for('toKey') == 'TOVALUE'      # value unaltered



class TestFieldsInfoFactory(object):

    default_args = {
        'alias_file': None,
        'collection': None,
        'debug': False,
        'db_config_file': None,
        'fields_file': None,
        'output_format': 'db',
        'processor_type': 'jwst',
        'verbose': False,
        'image_paths': [ '/images' ]
    }

    test_file = '/imdtk/tests/resources/test-fields.txt'
    empty_file = '/imdtk/tests/resources/empty.txt'
    comment_file = '/imdtk/tests/resources/test-fields-empty.txt'


    def test_ctor_no_fields_file (self):
        with pytest.raises(ValueError) as ve:
            fif = FieldsInfoFactory({})    # empty arguments dict
        print("VE={}".format(repr(ve)))
        assert ve.type == ValueError
        assert 'fields_file' in str(ve)
        assert 'missing' in str(ve)


    def test_ctor_with_fields_file (self):
        fif = FieldsInfoFactory({'debug': True, 'fields_file': self.test_file})


    def test_load_fields_info_empty (self):
        fif = FieldsInfoFactory({'verbose': True, 'fields_file': self.empty_file})
        fields = fif.load_fields_info()
        print("FIELDS={}".format(fields))
        assert len(fields) == 0
        assert 'equinox' not in fields


    def test_load_fields_info_comments (self):
        fif = FieldsInfoFactory({'verbose': True, 'fields_file': self.comment_file})
        fields = fif.load_fields_info()
        print("FIELDS={}".format(fields))
        assert len(fields) == 0
        assert 'equinox' not in fields


    def test_load_fields_info (self):
        fif = FieldsInfoFactory({'verbose': True, 'fields_file': self.test_file})
        fields = fif.load_fields_info()
        print("FIELDS={}".format(fields))
        assert len(fields) > 0
        assert 'equinox' in fields
