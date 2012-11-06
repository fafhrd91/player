import sys
from pyramid import testing
from pyramid.interfaces import IRequest
from pyramid.interfaces import IRequestExtensions

if sys.version_info[:2] == (2, 6):
    from unittest2 import TestCase
else:
    from unittest import TestCase


class BaseTestCase(TestCase):

    _include = True
    _auto_include = True
    _settings = {}
    _environ = {
        'wsgi.url_scheme':'http',
        'wsgi.version':(1,0),
        'HTTP_HOST': 'example.com',
        'SCRIPT_NAME': '',
        'PATH_INFO': '/'}
    registry = None

    def setUp(self):
        self.init_pyramid()

    def make_request(self, registry=None,
                     environ=None, request_iface=IRequest, **kwargs):
        if environ is None:
            environ=self._environ
        request = testing.DummyRequest(environ=dict(environ), **kwargs)
        request.request_iface = IRequest
        if registry is None:
            registry = self.registry
        if registry is not None:
            request.registry = registry
            request._set_extensions(registry.getUtility(IRequestExtensions))

        return request

    def init_extensions(self):
        from pyramid.config.factories import _RequestExtensions

        exts = self.registry.queryUtility(IRequestExtensions)
        if exts is None:
            exts = _RequestExtensions()
            self.registry.registerUtility(exts, IRequestExtensions)

    def init_pyramid(self):
        self.request = request = self.make_request()
        self.config = testing.setUp(
            request=request,
            settings=self._settings,
            autocommit=self._auto_include)
        self.config.get_routes_mapper()
        self.registry = self.config.registry
        self.init_extensions()

        self.request.registry = self.registry
        self.request._set_extensions(
            self.registry.getUtility(IRequestExtensions))

        if self._include:
            self.config.include('pyramid_layer')
