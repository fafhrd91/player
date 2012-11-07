""" layout implementation """
import sys
import json
import logging
import random
import inspect
import venusian
from collections import namedtuple
from zope.interface import providedBy, Interface
from pyramid.compat import text_, string_types
from pyramid.config.views import DefaultViewMapper
from pyramid.httpexceptions import HTTPException
from pyramid.location import lineage
from pyramid.registry import Introspectable
from pyramid.renderers import RendererHelper
from pyramid.interfaces import IRequest, IRouteRequest, IView, IViewClassifier

try:
    from collections import OrderedDict
except ImportError: # pragma no cover
    from ordereddict import OrderedDict


log = logging.getLogger('player')

LAYOUT_ID = 'player:layout'

LayoutInfo = namedtuple(
    'LayoutInfo', 'name layout view original renderer intr')

CodeInfo = namedtuple(
    'Codeinfo', 'filename lineno function source module')


class ILayout(Interface):
    """ marker interface """


def query_layout(root, context, request, name=''):
    """ query named layout for context """
    assert IRequest.providedBy(request), "must pass in a request object"

    try:
        iface = request.request_iface
    except AttributeError:
        iface = IRequest

    root = providedBy(root)

    adapters = request.registry.adapters

    for context in lineage(context):
        layout_factory = adapters.lookup(
            (root, iface, providedBy(context)), ILayout, name=name)

        if layout_factory is not None:
            return layout_factory, context

    return None, None


def query_layout_chain(root, context, request, layoutname=''):
    chain = []

    layout, layoutcontext = query_layout(root, context, request, layoutname)
    if layout is None:
        return chain

    chain.append((layout, layoutcontext))
    contexts = {layoutname: layoutcontext}

    while layout is not None and layout.layout is not None:
        if layout.layout in contexts:
            l_context = contexts[layout.layout].__parent__
        else:
            l_context = context

        layout, layoutcontext = query_layout(
            root, l_context, request, layout.layout)
        if layout is not None:
            chain.append((layout, layoutcontext))
            contexts[layout.name] = layoutcontext

            if layout.layout is None:
                break

    return chain


def add_layout(cfg, name='', context=None, root=None, parent=None,
               renderer=None, route_name=None, use_global_views=True,
               view=None):
    """Registers a layout.

    :param name: Layout name
    :param context: Specific context for this layout.
    :param root:  Root object
    :param parent: A parent layout. None means no parent layout.
    :param renderer: A pyramid renderer
    :param route_name: A pyramid route_name. Apply layout only for
        specific route
    :param use_global_views: Apply layout to all routes. even is route
        doesnt use use_global_views.
    :param view: View callable


    Simple example with one default layout and 'page' layout.

    .. code-block:: python

      class PageLayout(object):
           ...

      config.add_layout('page', parent='page', renderer='my_package:template/page.pt')


    To use layout with pyramid view use ``wrapper=player.wrap_layout()``

    Example:

    .. code-block:: python

      config.add_view('
          index.html',
          wrapper=player.wrap_layout(),
          renderer = '...')

    in this example '' layout is beeing used. You can specify specific layout
    name for pyramid view ``player.wrap_layout('page')``

    """
    (scope, module,
     f_locals, f_globals, codeinfo) = venusian.getFrameInfo(sys._getframe(2))

    codeinfo = CodeInfo(
        codeinfo[0], codeinfo[1], codeinfo[2], codeinfo[3], module.__name__)

    discr = (LAYOUT_ID, name, context, route_name)

    intr = Introspectable(LAYOUT_ID, discr, name, 'player_layout')

    intr['name'] = name
    intr['context'] = context
    intr['root'] = root
    intr['renderer'] = renderer
    intr['route_name'] = route_name
    intr['parent'] = parent
    intr['use_global_views'] = use_global_views
    intr['view'] = view
    intr['codeinfo'] = codeinfo

    if not parent:
        parent = None
    elif parent == '.':
        parent = ''

    if isinstance(renderer, string_types):
        renderer = RendererHelper(name=renderer, registry=cfg.registry)

    if context is None:
        context = Interface

    def register():
        request_iface = IRequest
        if route_name is not None:
            request_iface = cfg.registry.getUtility(
                IRouteRequest, name=route_name)

        if use_global_views:
            request_iface = Interface

        mapper = getattr(view, '__view_mapper__', DefaultViewMapper)
        mapped_view = mapper()(view)

        info = LayoutInfo(name, parent, mapped_view, view, renderer, intr)
        cfg.registry.registerAdapter(
            info, (root, request_iface, context), ILayout, name)

    cfg.action(discr, register, introspectables=(intr,))


class LayoutRenderer(object):

    def __init__(self, layout):
        self.layout = layout

    def layout_info(self, layout, context, request, content,
                    colors=('green','blue','yellow','gray','black')):
        intr = layout.intr
        view = intr['view']
        if view is not None:
            layout_factory = '%s.%s'%(view.__module__, view.__name__)
        else:
            layout_factory = 'None'

        data = OrderedDict(
            (('name', intr['name']),
             ('parent-layout', intr['parent']),
             ('layout-factory', layout_factory),
             ('python-module', intr['codeinfo'].module),
             ('python-module-location', intr['codeinfo'].filename),
             ('python-module-line', intr['codeinfo'].lineno),
             ('renderer', intr['renderer']),
             ('context', '%s.%s'%(context.__class__.__module__,
                                  context.__class__.__name__)),
             ('context-path', request.resource_url(context)),
             ))

        content = text_('\n<!-- layout:\n%s \n-->\n'\
                        '<div style="border: 2px solid %s">%s</div>')%(
            json.dumps(data, indent=2), random.choice(colors), content)

        return content

    def view_info(self, discr, context, request, content):
        introspector = request.registry.introspector

        template = 'unknown'
        intr = introspector.get('templates', discr)
        if intr is not None:
            template = intr['name']

        intr = introspector.get('views', discr)
        if intr is None:
            return content

        view = intr['callable']

        data = OrderedDict(
            (('name', intr['name']),
             ('route-name', intr['route_name']),
             ('view-factory', '%s.%s'%(view.__module__, view.__name__)),
             ('python-module', inspect.getmodule(view).__name__),
             ('python-module-location', inspect.getsourcefile(view)),
             ('python-module-line', inspect.getsourcelines(view)[-1]),
             ('renderer', template),
             ('context', '%s.%s'%(context.__class__.__module__,
                                  context.__class__.__name__)),
             ('context-path', request.resource_url(context)),
             ))

        content = text_('\n<!-- view:\n%s \n-->\n'\
                        '<div style="border: 2px solid red">%s</div>')%(
            json.dumps(data, indent=2), content)

        return content

    def __call__(self, context, request):
        chain = query_layout_chain(request.root, context, request, self.layout)
        if not chain:
            log.warning("Can't find layout '%s' for context '%s'",
                        self.layout, context)

        if isinstance(request.wrapped_response, HTTPException):
            return request.wrapped_response

        debug = getattr(request, '__layout_debug__', False)

        content = text_(request.wrapped_body, 'utf-8')

        if debug:
            content = self.view_info(debug, context, request, content)

        value = getattr(request, '__layout_data__', None)
        if value is None:
            value = {}

        for layout, layoutcontext in chain:
            if layout.view is not None:
                vdata = layout.view(layoutcontext, request)
                if vdata is not None:
                    value.update(vdata)

            system = {'view': getattr(request, '__view__', None),
                      'renderer_info': layout.renderer,
                      'context': layoutcontext,
                      'request': request,
                      'wrapped_content': content}

            content = layout.renderer.render(value, system, request)

            if debug:
                content = self.layout_info(
                    layout, layoutcontext, request, content)

        request.response.text = content
        return request.response


class Data(object): pass


def wrap_layout(layout=''):
    """ Generate view name for pyramid view declaration.

    .. code-block:: python

      config = Configurator()
      config.include('player')

      config.add_layout('page')

      config.add_view(
          'index.html',
          wrapper=player.wrap_layout())

    """
    lname = '#layout-{0}'.format(layout)

    def callback(context, name, ob):
        cfg = context.config.with_package(module)

        renderer = cfg.registry.adapters.lookup(
            (IViewClassifier, Interface, Interface), IView, name=lname)
        if renderer is None:
            cfg.registry.registerAdapter(
                LayoutRenderer(layout),
                (IViewClassifier, Interface, Interface), IView, lname)

    (scope, module,
     f_locals, f_globals, codeinfo) = venusian.getFrameInfo(sys._getframe(1))

    if not hasattr(module, '__layer_data__'):
        module.__layer_data__ = Data()

    venusian.attach(module.__layer_data__, callback, category='player')
    return lname


def set_layout_data(request, name, val):
    try:
        data = request.__layout_data__
    except:
        data = request.__layout_data__ = {}

    data[name] = val
