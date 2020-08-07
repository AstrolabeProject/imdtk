#
# Miscellaneous Utility Methods.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Add keep method (ala Clojure).
#
import json


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


def keep (fn, collection):
    """
    Returns a list of the non-None results of (fn item). Note, this means False
    return values will be included. The function should be free of side-effects.
    """
    return list(filter(lambda x: x is not None, map(fn, collection)))


def remove_entries (a_dictionary, ignore=[]):
    """
    Remove any entries whose keys are in the ignore list from the given dictionary.
    If not given, the ignore list defaults to an empty list.
    """
    for key in ignore:
        a_dictionary.pop(key, None)         # remove keyed entry: ignore key errors


def to_JSON (datadict, **json_kwargs):
    """
    Create and return a JSON string corresponding to the given data dictionary.

    :param json_kwargs: dictionary containing arguments to the json.dumps call.
    :return a JSON string
    """
    return json.dumps(datadict, **json_kwargs)
