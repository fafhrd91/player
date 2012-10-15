# pyramid_vlayer

from pyramid_vlayer.renderer import renderer
from pyramid_vlayer.renderer import template


def includeme(cfg):
    from pyramid.settings import asbool, aslist

    # settings
    settings = cfg.get_settings()
    settings['vlayer.order'] = [
        s.strip() for s in aslist(settings.get('vlayer.order', ''))]

    from pyramid_vlayer import vlayer, renderer

    # config directives
    cfg.add_directive('add_vlayer', vlayer.add_vlayer)
    #cfg.add_directive('add_vlayers', amd.add_js_module)

    # request
    from pyramid_vlayer.renderer import render_template

    cfg.add_request_method(render_template, 'render_tmpl')

    # renderer factory
    from pyramid_vlayer.renderer import vl_renderer_factory

    cfg.add_renderer('.vl', vl_renderer_factory)

    # scan
    cfg.scan('pyramid_vlayer')
