""" pvlayer command """
from __future__ import print_function
import os
import sys
import argparse
import textwrap
import tempfile
from pprint import pprint
from pyramid.compat import configparser, NativeIO, bytes_
from pyramid.path import AssetResolver
from pyramid.paster import bootstrap
from pyramid.threadlocal import get_current_registry


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')


def main():
    args = LayerCommand.parser.parse_args()
    cmd = LayerCommand(args)
    cmd.run()


class AmdjsCommand(object):

    parser = argparse.ArgumentParser(description="vlayer management")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    parser.add_argument('-b', action="store_true",
                        dest='build',
                        help='Build js bundles')

    parser.add_argument('-m', action="store_true",
                        dest='amd_mods',
                        help='List amd modules')

    parser.add_argument('--deps', action="store_true",
                        dest='deps',
                        help='Print dependency tree')

    parser.add_argument('--no-min', action="store_true",
                        dest='nomin',
                        help='Do not minimize js bundles')

    def __init__(self, args):
        self.options = args
        self.env = bootstrap(args.config)
        self.registry = self.env['registry']
        self.resolver = AssetResolver()

    def run(self):
        pass

