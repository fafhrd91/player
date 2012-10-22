# pyramid_vlayer

from pyramid_vlayer.renderer import renderer
from pyramid_vlayer.renderer import template


def includeme(cfg):
    import os
    from pyramid.path import AssetResolver
    from pyramid.settings import asbool, aslist
    from pyramid.exceptions import ConfigurationError

    from pyramid_vlayer import vlayer, renderer

    # settings
    settings = cfg.get_settings()
    settings['vlayer.order'] = [
        s.strip() for s in aslist(settings.get('vlayer.order', ''))]

    # config directives
    cfg.add_directive('add_vlayer', vlayer.add_vlayer)
    cfg.add_directive('add_vlayers', vlayer.add_vlayers)

    # request
    from pyramid_vlayer.renderer import render_template

    cfg.add_request_method(render_template, 'render_tmpl')

    # renderer factory
    from pyramid_vlayer.renderer import vl_renderer_factory

    cfg.add_renderer('.vl', vl_renderer_factory)

    # scan
    cfg.scan('pyramid_vlayer')

    # order
    order = {}
    for key, val in settings.items():
        if key.startswith('vlayer.order:'):
            layer = key[13:]
            order[layer] = [s.strip() for s in aslist(val)]

    if order:
        cfg.action(
            'pyramid_vlayer.order',
            vlayer.change_layers_order, (cfg, order), order=999999+1)

    # custom
    custom = settings.get('vlayer.custom', '').strip()
    if custom:
        resolver = AssetResolver()
        directory = resolver.resolve(custom).abspath()
        if not os.path.isdir(directory):
            raise ConfigurationError(
                "Directory is required for vlayer.custom setting: %s"%custom)

        cfg.action(
            'pyramid_vlayer.custom',
            vlayer.add_vlayers, (cfg, 'vlayer_custom', custom), order=999999+2)
