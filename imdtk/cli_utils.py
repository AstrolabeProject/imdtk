#
# Class defining utility methods for tool components CLI.
#   Written by: Tom Hicks. 6/1/2020.
#   Last Modified: Comment out output format argument as JSON is currently the only output format.
#
import argparse


def add_shared_arguments (parser, tool_name, version):
    """ Add the argument shared by all tools to the given argparse parser object. """
    parser.add_argument(
        '--version', action='version', version="{} version {}".format(tool_name, version),
        help='Show version information and exit.'
    )

    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        default=False,
        help='Print debugging output during processing [default: False (non-debug mode)]'
    )

    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        default=False,
        help='Print informational messages during processing [default: False (non-verbose mode)].'
    )


def add_output_arguments (parser, tool_name, version):
    """ Add common output arguments to the given argparse parser object. """
    parser.add_argument(
        '-g', '--generate', dest='gen_file_path', action='store_true',
        default=False,
        help='Automatically generate the output filename and path. [default: False].'
    )

    # parser.add_argument(
    #     '-os', '--output-sink', dest='output_sink', nargs='?',
    #     default='stdout',
    #     choices=['file', 'genfile', 'stdout'],
    #     help='Where to send the results of processing [default: stdout (standard output)]'
    # )

    parser.add_argument(
        '-of', '--output_file', dest='output_file', metavar='path_to_output_file',
        default=argparse.SUPPRESS,
        help='File path of file to hold the processing results [default: (standard output)]'
    )

    # parser.add_argument(
    #     '-ofmt', '--output-format', dest='output_format',
    #     default='json',
    #     choices=['json', 'other'],
    #     help='Output format for results: "json" or "other" [default: "json"]'
    # )


def add_input_arguments (parser, tool_name, version):
    """ Add common input arguments to the given argparse parser object. """
    parser.add_argument(
        '-ifmt', '--input-format', dest='input_format',
        default='json',
        choices=['json', 'text'],
        help='Format of input data file: "json" or "text" [default: "json"]'
    )

    parser.add_argument(
        '-if', '--input_file', dest='input_file', metavar='path_to_input_file',
        default=argparse.SUPPRESS,
        help='Path to a readable data file to be processed [default: (standard input)]'
    )
