#
# Miscellaneous Utility Methods.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Add method to get nested value from dictionary.
#

def get_in (a_dictionary, keys):
    """
    Get a nested value from the given dictionary indexed by the given sequence of keys.
    """
    dic = a_dictionary
    last_idx = len(keys) - 1
    for idx, key in enumerate(keys):
        val = dic.get(key)
        if (val is None):
            return None
        elif (idx >= last_idx):
            return val
        elif (isinstance(val, dict)):
            dic = val
        else:
            return None


def remove_entries (a_dictionary, ignore=[]):
    """
    Remove any entries whose keys are in the ignore list from the given dictionary.
    If not given, the ignore list defaults to an empty list.
    """
    for key in ignore:
        a_dictionary.pop(key, None)         # remove keyed entry: ignore key errors
