# pyramid_layer public api

from pyramid_layer.layer import tmpl_filter
from pyramid_layer.renderer import render, RendererNotFound


def includeme(cfg):
    import os
    from pyramid.path import AssetResolver
    from pyramid.settings import aslist
    from pyramid.exceptions import ConfigurationError

    from pyramid_layer.renderer import lt_renderer_factory
    from pyramid_layer.layer import add_layer, add_layers, change_layers_order
    from pyramid_layer.layer import add_tmpl_filter

    # config directives
    cfg.add_directive('add_layer', add_layer)
    cfg.add_directive('add_layers', add_layers)
    cfg.add_directive('add_tmpl_filter', add_tmpl_filter)

    # request.render_tmpl
    cfg.add_request_method(render, 'render_tmpl')

    # renderer factory
    cfg.add_renderer('.lt', lt_renderer_factory)

    # scan
    cfg.scan('pyramid_layer')

    # order
    settings = cfg.get_settings()

    order = {}
    for key, val in settings.items():
        if key.startswith('layer.order.'):
            layer = key[12:]
            order[layer] = [s.strip() for s in aslist(val)]

    if order:
        cfg.action(
            'pyramid_layer.order',
            change_layers_order, (cfg, order), order=999999+1)

    # custom
    custom = settings.get('layer.custom', '').strip()
    if custom:
        resolver = AssetResolver()
        directory = resolver.resolve(custom).abspath()
        if not os.path.isdir(directory):
            raise ConfigurationError(
                "Directory is required for layer.custom setting: %s"%custom)

        cfg.action(
            'pyramid_layer.custom',
            add_layers, (cfg, 'layer_custom', custom), order=999999+2)
