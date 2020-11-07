import collections

# class to hold an individual metadatum, a list of which is the metadata
Metadatum = collections.namedtuple('Metadatum', ['keyword', 'value'])

# class to hold an offsets and length information for FITS headers
FitsHeaderInfo = collections.namedtuple('FitsHeaderInfo', ['offset', 'length', 'hdr'])
