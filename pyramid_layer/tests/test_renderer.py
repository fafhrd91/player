from base import BaseTestCase


class TestRequestRenderers(BaseTestCase):

    def setUp(self):
        super(TestRequestRenderers, self).setUp()

        self.cfg = self.registry.settings

        from pyramid.interfaces import IRequestExtensions
        extensions = self.registry.getUtility(IRequestExtensions)
        self.request._set_extensions(extensions)

    def make_request(self):
        from pyramid.request import Request
        return Request(environ=self._environ)

    def test_render_tmpl(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        text = self.request.render_tmpl('test:view', object()).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_render_tmpl_with_filter(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        _calls = []
        def _filter(context, request):
            _calls.append((context, request))
            return {}

        self.config.add_tmpl_filter('test:view', _filter)

        ob = object()
        text = self.request.render_tmpl('test:view', ob).strip()
        self.assertEqual(text, '<h1>Test</h1>')
        self.assertEqual(1, len(_calls))
        self.assertEqual((ob, self.request), _calls[0])

    def test_render_tmpl_ext(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        text = self.request.render_tmpl('test:view.lt', object()).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_render_tmpl_unknown(self):
        self.assertRaises(
            ValueError, self.request.render_tmpl, 'test:view')

        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')
        self.assertRaises(
            ValueError, self.request.render_tmpl, 'test:view2')

    def test_render_tmpl_customize(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')
        self.config.add_layer(
            'test', 'custom', path='pyramid_layer:tests/bundle/dir1/')

        text = self.request.render_tmpl('test:view', object()).strip()
        self.assertEqual(text, '<h2>Test</h2>')

    def test_template(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        from pyramid_layer.renderer import template
        tmpl = template('test:view')

        text = tmpl(self.request, object())
        self.assertEqual(text, '<h1>Test</h1>')

    def test_pyramid_renderer(self):
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        from pyramid.renderers import render

        text = render('test:view.lt', {'context': object()}).strip()
        self.assertEqual(text, '<h1>Test</h1>')

    def test_pyramid_renderer_no_templates(self):
        """
        Raise ValueError if template can't be found.
        """
        self.config.add_layer(
            'test', path='pyramid_layer:tests/dir1/')

        from pyramid.renderers import render

        self.assertRaises(
            ValueError, render, 'test:view2.lt', {})

        self.assertRaises(
            ValueError, render, 'test1:view.lt', {})
