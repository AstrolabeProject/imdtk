#
# Miscellaneous Utility Methods.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Initial creation.
#

def remove_entries (a_dictionary, ignore=[]):
    """
    Remove any entries whose keys are in the ignore list from the given dictionary.
    If not given, the ignore list defaults to an empty list.
    """
    for key in ignore:
        a_dictionary.pop(key, None)         # remove keyed entry: ignore key errors
