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
    intr['asset'] = path
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


def change_layers_order(cfg, info):
    """ change layers order """
    storage = cfg.registry.setdefault(ID_VLAYER, {})
    for name, layers in info.items():
        data = storage.get(name)
        if not data:
            log.warning('vlayer.order:%s setting is not found'%name)
            continue

        def in_data(name, data):
            for intr in data:
                if intr['name'] == name:
                    return intr
            return None

        new_data = []
        for l in layers:
            intr = in_data(l, data)
            if intr:
                new_data.append(intr)

        new_data.extend([intr for intr in data if intr not in new_data])

        storage[name] = new_data
