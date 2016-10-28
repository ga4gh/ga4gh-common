"""
Common cli functionality
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import operator


class SortedHelpFormatter(argparse.HelpFormatter):
    """
    An argparse HelpFormatter that sorts the flags and subcommands
    in alphabetical order
    """
    def add_arguments(self, actions):
        """
        Sort the flags alphabetically
        """
        actions = sorted(
            actions, key=operator.attrgetter('option_strings'))
        super(SortedHelpFormatter, self).add_arguments(actions)

    def _iter_indented_subactions(self, action):
        """
        Sort the subcommands alphabetically
        """
        try:
            get_subactions = action._get_subactions
        except AttributeError:
            pass
        else:
            self._indent()
            if isinstance(action, argparse._SubParsersAction):
                for subaction in sorted(
                        get_subactions(), key=lambda x: x.dest):
                    yield subaction
            else:
                for subaction in get_subactions():
                    yield subaction
            self._dedent()


def addSubparser(subparsers, subcommand, description):
    """
    Add a subparser with subcommand to the subparsers object
    """
    parser = subparsers.add_parser(
        subcommand, description=description, help=description)
    return parser


def createArgumentParser(description):
    """
    Create an argument parser
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=SortedHelpFormatter)
    return parser
