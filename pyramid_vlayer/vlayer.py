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
    layers.insert(0, intr)

    cfg.action(discr, introspectables=(intr,))
    log.info("Add vlayer: %s path:%s"%(layer, directory))


def add_vlayers(cfg, name='', path='', description=''):
    """ add new vlayers, read directory use first level folders
    as layer name

    :param name: name
    :param path: asset path
    :param description: module description
    """
    resolver = AssetResolver()
    directory = resolver.resolve(path).abspath()

    for layer in os.listdir(directory):
        layer_path = os.path.join(directory, layer)
        if os.path.isdir(layer_path):
            add_vlayer(cfg, layer, name, layer_path, description)
