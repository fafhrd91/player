import os
import venusian
from pyramid.decorator import reify
from pyramid.interfaces import IRendererFactory
from pyramid.renderers import RendererHelper
from pyramid.threadlocal import get_current_registry

from .vlayer import ID_VLAYER

ID_TEMPLATE = 'pyramid_vlayer:template'


def render(request, asset, context=None, **options):
    registry = request.registry

    if context is not None:
        options['context'] = context

    templates = registry.get(ID_TEMPLATE)
    if templates is None:
        templates = registry[ID_TEMPLATE] = {}

    if asset not in templates:
        templates[asset] = renderer(asset)

    view = getattr(request, '__view__', None)
    if view is None:
        view = context

    request.__view__ = view

    options['view'] = view
    system = {'view': view,
              'renderer_info': templates[asset],
              'context': context,
              'request': request}

    result = templates[asset].render(options, None, request)

    request.__view__ = view
    return result


class template(object):

    def __init__(self, asset):
        self.asset = asset

    def __call__(self, request, context=None, **options):
        return render(request, self.asset, context, **options)


class renderer(RendererHelper):

    def __init__(self, asset):
        layer, name = asset.split(':', 1)
        self.layer = layer
        self.name = name
        self.package = None
        self.type = None

    @reify
    def registry(self):
        return get_current_registry()

    @reify
    def renderer(self):
        registry = self.registry

        storage = registry.get(ID_VLAYER)
        if not storage or self.layer not in storage:
            raise ValueError('Layer is not found: "%s"'%self.layer)

        factories = dict(
            (name, factory) for name, factory in
            registry.getUtilitiesFor(IRendererFactory) if name.startswith('.'))

        layer = storage[self.layer]

        for intr in layer:
            for ext, factory in factories.items():
                fname = os.path.join(intr['path'], '%s%s'%(self.name, ext))
                if os.path.exists(fname):
                    self.type = ext
                    self.name = fname
                    return factory(self)

        raise ValueError(
            'Missing template layer renderer: %s:%s' % (self.layer, self.name))


def vl_renderer_factory(info):
    registry = info.registry

    layer, name = info.name.split(':', 1)
    name = name[:-3]

    storage = registry.get(ID_VLAYER)
    if not storage or layer not in storage:
        raise ValueError('Layer is not found: "%s"'%layer)

    factories = dict(
        (name, factory) for name, factory in
        registry.getUtilitiesFor(IRendererFactory) if name.startswith('.'))

    layer = storage[layer]

    for intr in layer:
        for ext, factory in factories.items():
            fname = os.path.join(intr['path'], '%s%s'%(name, ext))
            if os.path.exists(fname):
                info.name = fname
                return factory(info)

    raise ValueError(
        'Missing template layer renderer: %s:%s' % (layer, name))
