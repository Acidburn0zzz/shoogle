"""Use the Google API from the command-line."""
import argparse
import json
import logging
import sys

import oauth2client.client
import googleapiclient.errors
import googleapiclient.discovery

from . import __version__
from . import lib
from . import common
from .commands import show
from .commands import execute

DEFAULT_LOGGER = lib.get_logger("shoogle", level=logging.ERROR, channel=sys.stderr)

def get_parser(description):
    """Return an ArgumentParser for the command-line app."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-v', '--version', action="store_true",
                        help="Show application version and exit")

    subparsers = parser.add_subparsers(help='Commands', dest="command")
    subparsers.required = False
    show.add_parser(subparsers, "show")
    execute.add_parser(subparsers, "execute")
    return parser

def run(args):
    """Parse options and run shoogle commands. Return status code."""
    parser = get_parser("Command-line interface for the Google API.")
    try:
        options = parser.parse_args(args)
    except SystemExit:
        return 2

    if options.version:
        lib.output(__version__)
        return 0
    elif options.command == "show":
        show.run(options)
        return 0
    elif options.command == "execute":
        execute.run(options)
        return 0
    else:
        parser.print_help(sys.stderr)
        return 2

def main(args, logger=DEFAULT_LOGGER):
    """Run shoogle with command-line arguments and return status code."""
    try:
        return run(args)
    except common.ShoogleException as error:
        logger.error(error)
        return 1
    except googleapiclient.errors.HttpError as error:
        status = error.resp["status"]
        data = bytes.decode(error.content).strip()
        logger.error("Server error response ({0}): {1}".format(status, data))
        return 1
    except oauth2client.client.FlowExchangeError as error:
        logger.error("OAuth 2 error: {}".format(error))
    except json.decoder.JSONDecodeError as error:
        logger.error("JSONDecodeError: " + str(error))
        logger.error("JSON was: " + error.doc)
        return 1

if __name__ == '__main__':
    sys.exit(run(sys.argv[:1]))
