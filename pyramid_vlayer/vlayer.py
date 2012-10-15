import os
import logging
from pyramid.path import AssetResolver
from pyramid.registry import Introspectable
from pyramid.exceptions import ConfigurationError

log = logging.getLogger('pyramid_vlayer')

ID_VLAYER = 'pyramid_vlayer:vlayer'


def add_vlayer(cfg, layer, name='', path='', description=''):
    """ add new vlayer

    :param layer: layer id
    :param name: name
    :param path: asset path
    :param description: module description
    """
    discr = (ID_VLAYER, name, layer)

    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    intr = Introspectable(ID_VLAYER, discr, name, ID_VLAYER)
    intr['name'] = name
    intr['layer'] = layer
    intr['path'] = directory
    intr['description'] = description

    storage = cfg.registry.setdefault(ID_VLAYER, {})
    layers = storage.setdefault(layer, [])
    layers.append(intr)

    cfg.action(discr, introspectables=(intr,))
    log.info("Add vlayer: %s path:%s"%(layer, directory))
