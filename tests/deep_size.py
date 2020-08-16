from collections import Mapping, Container
from sys import getsizeof

def deep_getsizeof(obj, ids=set()):
    """Find the memory footprint of a Python object

    This is a recursive function that drills down a Python object graph
    like a dictionary holding nested dictionaries with lists of lists
    and tuples and sets.

    The sys.getsizeof function does a shallow size of only. It counts each
    object inside a container as pointer only regardless of how big it
    really is.

    :param obj: the object
    :param ids:
    :return:
    """
    d = deep_getsizeof
    if id(obj) in ids:
        return 0

    r = getsizeof(obj)
    ids.add(id(obj))

    if isinstance(obj, str) or isinstance(0, str):
        return r

    if isinstance(obj, Mapping):
        return r + sum(d(k, ids) + d(v, ids) for k, v in obj.items())

    if isinstance(obj, Container):
        return r + sum(d(x, ids) for x in obj)

    return r
