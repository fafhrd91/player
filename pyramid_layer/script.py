""" player command """
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
from pyramid.interfaces import IRendererFactory

from .layer import ID_LAYER


grpTitleWrap = textwrap.TextWrapper(
    initial_indent='* ',
    subsequent_indent='  ')

grpDescriptionWrap = textwrap.TextWrapper(
    initial_indent='    ',
    subsequent_indent='    ')

grpThirdLevelWrap = textwrap.TextWrapper(
    initial_indent='      ',
    subsequent_indent='      ', width=250)


def main():
    args = LayersCommand.parser.parse_args()
    cmd = LayersCommand(args)
    cmd.run()


class LayersCommand(object):

    parser = argparse.ArgumentParser(description="player management")
    parser.add_argument('config', metavar='config',
                        help='ini config file')

    parser.add_argument('-l', action="store_true",
                        dest='list',
                        help='List layers')

    parser.add_argument('-lt', action="store_true",
                        dest='list_tmpls',
                        help='List templates')

    parser.add_argument('asset', metavar='asset', nargs='*',
                        help='Layer\template id')

    def __init__(self, args):
        self.options = args
        self.env = bootstrap(args.config)
        self.registry = self.env['registry']
        self.resolver = AssetResolver()

    def run(self):
        if self.options.list:
            self.list_layers()
        elif self.options.list_tmpls:
            self.list_templates()
        else:
            self.parser.print_help()

    def list_layers(self):
        storage = self.registry.get(ID_LAYER)
        if not storage:
            print ('No layers are found.')
            return

        print()

        storage = sorted(storage.items())
        filter = [s.strip().split(':',1)[0] for s in self.options.asset]

        for name, layers in storage:
            if filter and name not in filter:
                continue

            print(grpTitleWrap.fill('Layer: %s'%name))

            for layer in layers:
                print(grpDescriptionWrap.fill('name: %s'%layer['name']))
                print(grpDescriptionWrap.fill('path: %s'%layer['asset']))

            print()

    def list_templates(self):
        storage = self.registry.get(ID_LAYER)
        if not storage:
            print ('No layers are found.')
            return

        print()

        storage = sorted(storage.items())
        f_layers = [s.strip().split(':',1)[0] for s in self.options.asset]

        factories = dict(
            (name, factory) for name, factory in
            self.registry.getUtilitiesFor(IRendererFactory)
            if name.startswith('.'))

        for name, layers in storage:
            if f_layers and name not in f_layers:
                continue

            print(grpTitleWrap.fill('Layer: %s'%name))

            tmpls = {}
            for layer in layers:
                for name in os.listdir(layer['path']):
                    if '.' in name:
                        rname, rtype = os.path.splitext(name)
                        key = (layer['asset'], rname)
                        if rtype in factories and key not in tmpls:
                            tmpls[key] = rtype

                curr_asset = None
                for (asset, rname), rtype in sorted(tmpls.items()):
                    if curr_asset != asset:
                        curr_asset = asset
                        print('')
                        print(grpDescriptionWrap.fill(asset))

                    if rname in layer['filters']:
                        f = layer['filters'][rname]
                        sinfo = ('%s.py: %s'%(
                            f.__module__.replace('.', '/'), f.__name__))
                        print(grpThirdLevelWrap.fill('%s: %s (%s)'%(
                            rname, rtype, sinfo)))
                    else:
                        print(grpThirdLevelWrap.fill('%s: %s'%(rname, rtype)))

            print()
